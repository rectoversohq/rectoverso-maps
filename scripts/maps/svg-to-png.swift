// Renders SVG files to PNG with WebKit (AppKit's SVG support drops parts of some flags,
// e.g. Brazil's green field). Each PNG is `height` px tall, keeping the SVG's aspect ratio.
//   swift svg-to-png.swift <out-dir> <height> <file.svg>…
import AppKit
import WebKit

let args = CommandLine.arguments
let outDir = URL(fileURLWithPath: args[1])
let height = CGFloat(Double(args[2])!)
let files = Array(args.dropFirst(3))

/// The SVG's aspect ratio, from its viewBox (or width/height attributes).
func aspect(of svg: String) -> CGFloat? {
    func attr(_ name: String) -> String? {
        guard let r = svg.range(of: "\(name)=\"([^\"]+)\"", options: .regularExpression) else { return nil }
        return String(svg[r]).components(separatedBy: "\"")[1]
    }
    if let box = attr("viewBox") {
        let n = box.split(whereSeparator: { $0 == " " || $0 == "," }).compactMap { Double($0) }
        if n.count == 4, n[3] > 0 { return CGFloat(n[2] / n[3]) }
    }
    if let w = attr("width").flatMap({ Double($0.filter { "0123456789.".contains($0) }) }),
       let h = attr("height").flatMap({ Double($0.filter { "0123456789.".contains($0) }) }), h > 0 {
        return CGFloat(w / h)
    }
    return nil
}

@MainActor
final class Renderer: NSObject, WKNavigationDelegate {
    let view = WKWebView(frame: .zero)
    var queue: [String]
    var current: (path: String, size: CGSize)?
    var failures = 0

    init(files: [String]) {
        queue = files
        super.init()
        view.navigationDelegate = self
        view.setValue(false, forKey: "drawsBackground")
    }

    func next() {
        guard let path = queue.first else {
            print("done, \(failures) failed")
            exit(failures == 0 ? 0 : 1)
        }
        queue.removeFirst()
        guard let svg = try? String(contentsOfFile: path, encoding: .utf8), let ratio = aspect(of: svg) else {
            print("FAIL (no size)", path); failures += 1; next(); return
        }
        let size = CGSize(width: (height * ratio).rounded(), height: height)
        current = (path, size)
        view.frame = CGRect(origin: .zero, size: size)
        // The SVG markup inline (as an <img> file, Brazil's flag failed to load), filling the
        // page exactly; no margins, transparent background.
        let markup = svg.replacingOccurrences(of: "<\\?xml[^>]*>", with: "", options: .regularExpression)
        let html = """
        <html><head><style>html,body{margin:0;background:transparent;overflow:hidden}\
        svg{display:block;width:\(Int(size.width))px;height:\(Int(size.height))px}</style></head>\
        <body>\(markup)</body></html>
        """
        view.loadHTMLString(html, baseURL: URL(fileURLWithPath: path).deletingLastPathComponent())
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        snapshot(attempt: 1)
    }

    func snapshot(attempt: Int) {
        guard let current else { return }
        let config = WKSnapshotConfiguration()
        config.rect = CGRect(origin: .zero, size: current.size)
        config.snapshotWidth = NSNumber(value: Double(current.size.width))
        view.takeSnapshot(with: config) { image, error in
            let name = (current.path as NSString).lastPathComponent.replacingOccurrences(of: ".svg", with: ".png")
            if let image, let tiff = image.tiffRepresentation, let rep = NSBitmapImageRep(data: tiff),
               let png = rep.representation(using: .png, properties: [:]) {
                do {
                    try png.write(to: outDir.appendingPathComponent(name))
                } catch {
                    print("FAIL (write)", current.path, error); self.failures += 1
                }
            } else {
                // WebKit can temporarily decline a snapshot even after navigation
                // completes. Bound retries; a failed render must never look successful.
                let detail = error.map(String.init(describing:)) ?? "no encodable image"
                if attempt < 3 {
                    print("RETRY snapshot \(attempt)", current.path, detail)
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.25) {
                        self.snapshot(attempt: attempt + 1)
                    }
                    return
                }
                print("FAIL snapshot", current.path, detail); self.failures += 1
            }
            self.next()
        }
    }

    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        print("FAIL navigation", current?.path ?? "unknown", error)
        failures += 1
        next()
    }

    func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
        self.webView(webView, didFail: navigation, withError: error)
    }
}

// Top-level code runs on the main thread; say so, so the main-actor renderer can start.
nonisolated(unsafe) var renderer: Renderer?
MainActor.assumeIsolated {
    renderer = Renderer(files: files)
    renderer?.next()
}
NSApplication.shared.run()
