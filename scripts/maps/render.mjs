// Draw the frozen roster in Night style and write every RectoVerso place field.
// node render.mjs <places.geojson> <places.json> <50m-context.geojson> <output-dir>
import fs from "node:fs";
import path from "node:path";
import * as d3 from "d3-geo";

const [, , detailedPath, rosterPath, contextPath, out, neutralPath] = process.argv;
const roster = JSON.parse(fs.readFileSync(rosterPath, "utf8"));
const detailed = JSON.parse(fs.readFileSync(detailedPath, "utf8")).features;
const context = JSON.parse(fs.readFileSync(contextPath, "utf8")).features;
const neutral = neutralPath ? JSON.parse(fs.readFileSync(neutralPath, "utf8")).features : [];
const W = 1200, H = 900;
const GOLD = "#F2C14E";

// Natural Earth's subregions, in French (the region VoiceOver says).
const REGION_FR = {
  "Australia and New Zealand": "Australie et Nouvelle-Zélande", "Caribbean": "Caraïbes", "Central America": "Amérique centrale",
  "Central Asia": "Asie centrale", "Eastern Africa": "Afrique de l'Est", "Eastern Asia": "Asie de l'Est", "Eastern Europe": "Europe de l'Est",
  "Melanesia": "Mélanésie", "Micronesia": "Micronésie", "Middle Africa": "Afrique centrale", "Northern Africa": "Afrique du Nord",
  "Northern America": "Amérique du Nord", "Northern Europe": "Europe du Nord", "Polynesia": "Polynésie", "South America": "Amérique du Sud",
  "South-Eastern Asia": "Asie du Sud-Est", "Southern Africa": "Afrique australe", "Southern Asia": "Asie du Sud", "Southern Europe": "Europe du Sud",
  "Western Africa": "Afrique de l'Ouest", "Western Asia": "Asie de l'Ouest", "Western Europe": "Europe de l'Ouest", "Antarctica": "Antarctique", "Seven seas (open ocean)": "Océans",
};

// The approved Night pipeline frames the primary landmass and substantial nearby
// parts. Widely scattered archipelagos and the antimeridian challenge cases keep
// all parts in the picture's frame. The field always retains the full geometry.
const WHOLE_PLACE = new Set(["KIR", "FJI", "RUS", "IDN", "FSM", "BES", "SJM", "SHN", "UMI", "ATF", "SGS", "TKL", "HMD", "PCN", "PRT"]);
function focus(feature) {
  if (feature.properties.wholeQuestion || WHOLE_PLACE.has(feature.properties.code) || feature.geometry.type !== "MultiPolygon") return feature;
  const parts = feature.geometry.coordinates.map(c => ({type:"Polygon",coordinates:c}));
  const main = parts.reduce((a,b) => d3.geoArea(b)>d3.geoArea(a)?b:a);
  const center = d3.geoCentroid(main);
  const near = parts.filter(p => d3.geoDistance(d3.geoCentroid(p),center)<0.35 && d3.geoArea(p)>d3.geoArea(main)*0.002);
  return {type:"Feature",geometry:{type:"MultiPolygon",coordinates:near.map(p=>p.coordinates)}};
}

// Frame the selected focus, including both sides of the antimeridian. The midpoint of d3's
// wrapped longitude bounds avoids centering a scattered archipelago on its largest island.
function projection(feature, width = W, height = H, whole = false, close = false) {
  if (feature.properties.code === "ATA") return d3.geoAzimuthalEqualArea()
    .rotate([0, 90]).clipAngle(100).fitExtent([[60,50],[width-60,height-50]], feature);
  feature = whole ? feature : focus(feature);
  const [[west, south], [east, north]] = d3.geoBounds(feature);
  const unwrappedEast = east < west ? east + 360 : east;
  let lon = (west + unwrappedEast) / 2;
  if (lon > 180) lon -= 360;
  const center = [lon, (south + north) / 2];
  if ((whole || WHOLE_PLACE.has(feature.properties?.code)) && !close) return d3.geoAzimuthalEqualArea().rotate([-center[0],-center[1]])
    .clipAngle(150).fitExtent([[width*.1,height*.12],[width*.9,height*.88]],feature);
  const points = feature.geometry.type === "Polygon"
    ? feature.geometry.coordinates.flat() : feature.geometry.coordinates.flat(2);
  const radius = Math.max(...points.map(p => d3.geoDistance(center, p))) * 180 / Math.PI;
  const reach = close ? Math.max(0.06, radius * 1.35) : Math.min(145, Math.max(radius * (radius < 3 ? 1.8 : 2.2), radius < 3 ? 4 : 7));
  return d3.geoAzimuthalEqualArea().rotate([-center[0], -center[1]]).clipAngle(150)
    .fitExtent([[0, 0], [width, height]], d3.geoCircle().center(center).radius(reach)());
}

// The rings that show where a place too small to see is (Monaco, Tuvalu's atolls): one around
// each of its parts, parts whose rings would touch sharing one oval round all of them. None when the place reads on its own.
function rings(draw, feature, pad = 22, min = 32) {
  const [[bx0, by0], [bx1, by1]] = draw.bounds(feature);
  const g = feature.geometry;
  const parts = (g.type === "Polygon" ? [g.coordinates] : g.coordinates).map(c => ({ type: "Polygon", coordinates: c }));
  const size = part => { const [[x0, y0], [x1, y1]] = draw.bounds(part); return Math.max(x1 - x0, y1 - y0); };
  // Small as a whole, or only specks however far they spread (Tuvalu, Kiribati: their largest
  // island under 14 px).
  if (Math.max(bx1 - bx0, by1 - by0) >= 60 && Math.max(...parts.map(size)) >= 14 && Math.max(...parts.map(part => draw.area(part))) >= 500) return [];
  // Each part a box; boxes whose rings would touch merge, until none do. Each group then gets an
  // oval round its box: a circle for one island, a long oval for a chain (the Maldives).
  let groups = parts.map(part => draw.bounds(part)).filter(b => b.flat().every(isFinite))
    .map(([[x0, y0], [x1, y1]]) => ({ x0, y0, x1, y1 }));
  const reach = g => ({ rx: Math.max(min, (g.x1 - g.x0) / 2 + pad), ry: Math.max(min, (g.y1 - g.y0) / 2 + pad) });
  const touch = (a, b) => {
    const ra = reach(a), rb = reach(b);
    return Math.abs((a.x0 + a.x1) / 2 - (b.x0 + b.x1) / 2) < ra.rx + rb.rx + 6 && Math.abs((a.y0 + a.y1) / 2 - (b.y0 + b.y1) / 2) < ra.ry + rb.ry + 6;
  };
  for (let merged = true; merged;) {
    merged = false;
    outer: for (let i = 0; i < groups.length; i++) for (let j = i + 1; j < groups.length; j++) {
      if (!touch(groups[i], groups[j])) continue;
      const [a, b] = [groups[i], groups[j]];
      groups[i] = { x0: Math.min(a.x0, b.x0), y0: Math.min(a.y0, b.y0), x1: Math.max(a.x1, b.x1), y1: Math.max(a.y1, b.y1) };
      groups.splice(j, 1);
      merged = true;
      break outer;
    }
  }
  return groups.map(g => [(g.x0 + g.x1) / 2, (g.y0 + g.y1) / 2, reach(g).rx, reach(g).ry]);
}

function view(feature, width, height, close = false, whole = false, locatorGroups = [], parent) {
  const frame = feature.properties?.regionalContext
    ? {type:"Feature", properties:{code:feature.properties.parentCode}, geometry:feature.properties.regionalContext} : feature;
  const p = projection(frame, width, height, whole, close), draw = d3.geoPath(p);
  // Do not draw a second, coarser coastline underneath the highlighted entry.
  // The 50m Netherlands feature still combines the Caribbean Netherlands.
  const entryCode = parent.properties.parentCode || parent.properties.code;
  const contextCode = ({BES:"NLD",SJM:"NOR",GUF:"FRA",GLP:"FRA",MTQ:"FRA",MYT:"FRA",REU:"FRA"})[entryCode] || entryCode;
  const neighbours = context.flatMap(f => {
    if (f.properties.ADM0_A3 !== contextCode) return [f];
    const parts = f.geometry.type === "Polygon" ? [f.geometry.coordinates] : f.geometry.coordinates;
    const remaining = parts.filter(coordinates => !d3.geoContains(parent,d3.geoCentroid({type:"Polygon",coordinates})));
    return remaining.length ? [{type:"MultiPolygon",coordinates:remaining}] : [];
  })
    .map(f => `<path d="${draw(f) || ""}" fill="#3E5068" stroke="#5F7591" stroke-width="1.4"/>`).join("");
  // Meaningful island groups receive one locator each; never one ring per rock.
  const targets = locatorGroups.length ? locatorGroups : [feature];
  const ring = targets.flatMap(f => locatorGroups.length > 4 ? rings(draw,f,5,9) : locatorGroups.length ? rings(draw,f,9,15) : rings(draw,f)).map(([x,y,rx,ry]) => `<ellipse cx="${x}" cy="${y}" rx="${rx}" ry="${ry}" fill="none" stroke="${GOLD}" stroke-width="4"/>`).join("");
  const undetermined = neutral.map(f => `<path d="${draw(f) || ""}" fill="#506077" stroke="#506077" stroke-width="5"/><path d="${draw(f) || ""}" fill="none" stroke="#C3CDDB" stroke-width="2.4" stroke-dasharray="8 8"/>`).join("");
  return `<rect width="${width}" height="${height}" fill="url(#deep)"/><path d="${draw(d3.geoGraticule10())}" fill="none" stroke="#A9C6EA" stroke-opacity="0.2" stroke-width="1.2"/>${neighbours}<path d="${draw(feature)}" fill="${GOLD}" stroke="#F7DA8F" stroke-width="1.4"/>${undetermined}${ring}`;
}

function night(feature) {
  const groups = feature.properties.regionalContext
    ? [{type:"Feature", properties:{name:feature.properties.name}, geometry:feature.geometry}]
    : feature.properties.pictureGroups || [];
  const count = groups.length, rows = count > 4 ? 2 : 1, cols = Math.ceil(count / rows);
  const detailsHeight = count > 4 ? 420 : 300;
  const overviewHeight = count ? H - detailsHeight - 12 : H;
  let defs = `<linearGradient id="deep" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1F4C86"/><stop offset="1" stop-color="#16396A"/></linearGradient>`;
  let drawing = "";
  function panel(f, x, y, width, height, index, close, whole, locators) {
    const id = `panel-${index}`;
    defs += `<clipPath id="${id}"><rect width="${width}" height="${height}"/></clipPath>`;
    drawing += `<g transform="translate(${x},${y})"><g clip-path="url(#${id})">${view(f,width,height,close,whole,locators,feature)}</g></g>`;
  }
  panel(feature,0,0,W,overviewHeight,0,false,count>0 || feature.properties.wholeQuestion,groups);
  groups.forEach((group,i) => {
    const width = (W - (cols-1)*12)/cols, height = (detailsHeight-(rows-1)*12)/rows;
    panel(group,(i%cols)*(width+12),overviewHeight+12+Math.floor(i/cols)*(height+12),width,height,i+1,true,true,[]);
  });
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}"><defs>${defs}</defs><rect width="${W}" height="${H}" fill="#132C4D"/>${drawing}</svg>`;
}

// The preparer supplies the validated, topology-preserving field outline.
function outline(feature) {
  if (!feature.properties.fieldOutline) throw new Error("Missing validated field outline");
  return feature.properties.fieldOutline;
}

fs.mkdirSync(out, { recursive: true });
const places = [];
for (const entry of roster) {
  const feature = detailed.find(f => f.properties.code === entry.code);
  if (!feature) throw new Error(`Missing geometry: ${entry.code}`);
  const code = entry.code, region = entry.region;
  const regionFr = entry.regionHint?.fr || REGION_FR[region];
  if (!regionFr) throw new Error(`Missing French region: ${region}`);
  fs.writeFileSync(path.join(out, `${code}.svg`), night(feature));
  const field = { code, region: { en: region, fr: regionFr }, outline: outline(feature) };
  places.push({ ...entry, pictureFocus: entry.parentCode ? "parent-context-with-regional-detail" : entry.pictureGroups ? "whole-place-with-component-insets" : WHOLE_PLACE.has(code) ? "whole-place" : "primary-and-nearby", picture: `rv-map-${code.toLowerCase()}.png`, field: JSON.stringify(field) });
}
fs.writeFileSync(path.join(out, "places.json"), JSON.stringify(places, null, 2) + "\n");
console.log(`Drew ${places.length} maps and fields.`);
