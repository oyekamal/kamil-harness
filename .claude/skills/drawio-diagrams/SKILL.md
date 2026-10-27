---
name: drawio-diagrams
description: Generate real, editable draw.io (.drawio / diagrams.net) diagrams — flowcharts, architecture diagrams, lesson-plan visuals, mind maps, entity diagrams, and floor plans / building blueprints — as standalone XML files the user can open directly in app.diagrams.net or the desktop app. Triggers on "diagram", "flowchart", "blueprint", "floor plan", "draw.io", "diagrams.net", "architecture diagram", "mind map", "lesson plan visual", "org chart", "make a diagram of".
---

# Draw.io Diagrams

Technique vendored from [next-ai-draw-io](https://github.com/DayuanJiang/next-ai-draw-io) (35k★, MIT) — its prompting/XML-generation approach, not the Next.js app itself. This skill writes a complete `.drawio` file directly to disk; no server or app deployment needed. The user opens it in [app.diagrams.net](https://app.diagrams.net) (free, no login) or the draw.io desktop app.

## When to use

Any request for a real diagram deliverable, not a description of one: flowcharts, system/architecture diagrams, entity-relationship diagrams, org charts, mind maps, lesson-plan visuals (concept maps, process diagrams for teaching), and floor plans / building blueprints.

Prefer this over a text description or an ASCII sketch whenever the user wants something they can open, edit, and present. For an inline diagram *inside a Claude Code Artifact*, use `artifact-diagramming` (SVG/mermaid) instead — reach for this skill when the deliverable is a standalone file the user will open in draw.io/diagrams.net directly, edit further, or hand to someone else.

## Output

Write a complete, valid `.drawio` file:

```xml
<mxfile host="app.diagrams.net" modified="{{ISO_TIMESTAMP}}" agent="{{AGENT_NAME}}" version="21.5.2" type="device">
  <diagram id="page1" name="Page-1">
    <mxGraphModel dx="1" dy="1" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="850" pageHeight="1100" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <!-- your mxCell shapes and edges go here, id starting from "2" -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

Only the cells inside `<root>` after the two auto id="0"/id="1" cells are yours to generate.

## Core cell patterns

**Shape (vertex):**
```xml
<mxCell id="2" value="Label" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="120" height="60" as="geometry"/>
</mxCell>
```

**Connector (edge):**
```xml
<mxCell id="3" style="edgeStyle=orthogonalEdgeStyle;exitX=1;exitY=0.5;entryX=0;entryY=0.5;endArrow=classic;html=1;" edge="1" parent="1" source="2" target="4">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

Rules:
- All `mxCell` elements are siblings — never nest one inside another. Use `parent` to express containment (e.g. a swimlane's children set `parent="lane1"`, not nesting XML).
- Unique sequential ids starting at `"2"`.
- `parent="1"` for top-level shapes, or a container's id for grouped children.
- Escape XML entities in `value`: `&lt; &gt; &amp; &quot;`.
- No XML comments — draw.io strips them.

## Layout constraints (keep everything on one printable page)

- Keep coordinates within x: 0–800, y: 0–600 for a single-viewport diagram (bump `pageWidth`/`pageHeight` in `mxGraphModel` if a blueprint genuinely needs more room, e.g. a large floor plan).
- Container/group boxes: max width ~700px, max height ~550px.
- Space shapes 150–200px apart to leave clear routing channels for edges.
- Start from margins like x=40, y=40; group related elements closely; prefer vertical stacking or a grid for many elements over spreading wide.

## Edge routing rules (the part that's easy to get wrong)

Plan layout in your head *before* generating XML: lay shapes into columns/rows by flow direction, then trace each edge mentally — "what sits between source and target?"

1. **Never let two edges share the same path.** If two edges connect the same pair of nodes, offset them: `exitY=0.3` for one, `exitY=0.7` for the other — not both `0.5`.
2. **Bidirectional pairs (A↔B) use opposite sides.** A→B exits right (`exitX=1`) enters left (`entryX=0`); B→A exits left enters right.
3. **Always set all four of `exitX`/`exitY`/`entryX`/`entryY` explicitly** in the edge style — don't rely on draw.io's auto-routing guess.
4. **Route around obstacles.** If a shape sits between source and target, add waypoints (`<Array as="points"><mxPoint x=".." y=".."/></Array>` inside the edge's `mxGeometry`) to detour around it — 20–30px clearance from its bounding box. For diagonal connections, route along the diagram's perimeter, not through the middle.
5. **Plan for clear channels.** 150–200px shape spacing gives edges room to route orthogonally without crossing shapes.
6. **Multi-waypoint corners.** Complex routes need 2–3 waypoints forming clean L/U-shaped orthogonal segments — one waypoint per direction change.
7. **Never use corner connection points** (`entryX=1,entryY=1` etc.) — pick the side matching flow direction: top-to-bottom flow exits bottom (`exitY=1`) enters top (`entryY=0`); left-to-right exits right enters left.

Before finalizing, check: any edge crossing a non-endpoint shape? Any two edges sharing a path? Any corner connection points? Could rearranging shapes reduce crossings?

## Styling

Common style tokens (append to `style="..."`, semicolon-separated):
- Shapes: `rounded=1`, `fillColor=#hex`, `strokeColor=#hex`, `whiteSpace=wrap`, `html=1`
- Edges: `endArrow=classic|block|open|none`, `startArrow=none|classic`, `curved=1`, `edgeStyle=orthogonalEdgeStyle`
- Text: `fontSize=14`, `fontStyle=1` (bold), `align=center|left|right`
- Containers/swimlanes: `style="swimlane;"` — children get `parent="<lane-id>"`

For a minimal/plain look (no color, black-and-white only): drop all fill/stroke-color tokens, use `whiteSpace=wrap;html=1;` for shapes and `html=1;endArrow=classic;` for edges, and set container fills to `fillColor=none;` so they stay transparent over children.

## Building blueprints / floor plans

Use the `mxgraph.floorplan.*` shape family for furniture and fixtures:

```xml
<mxCell value="" style="shape=mxgraph.floorplan.bed_double;fillColor=#ffffff;strokeColor=#000000;" vertex="1" parent="1">
  <mxGeometry x="40" y="40" width="60" height="80" as="geometry"/>
</mxCell>
```

Available fixtures (45): `bathtub`, `bathtub2`, `bed_double`, `bed_single`, `bookcase`, `chair`, `office_chair`, `copier`, `couch`, `sofa`, `crt_tv`, `flat_tv`, `desk_corner`, `desk_corner_2`, `dresser`, `drying_machine`, `elevator`, `fireplace`, `floor_lamp`, `laptop`, `piano`, `plant`, `printer`, `range_1`, `range_2`, `refrigerator`, `shower`, `shower2`, `sink_1`, `sink_2`, `sink_22`, `sink_double`, `sink_double2`, `spiral_stairs`, `table` (+ `table_1`–`table_5`), `toilet`, `washing_machine`, `water_cooler`, `workstation`.

The library has no dedicated wall/door/window stencils — build the architectural shell with plain shapes:
- **Walls**: thin rectangles, `style="fillColor=#000000;strokeColor=none;"`, typically 10–15px thick, positioned as the room perimeter.
- **Doors**: a short wall gap plus a quarter-circle swing arc — `style="shape=mxgraph.floorplan.doorRight"` if unavailable, approximate with an `arc` style curve (`style="curved=1;endArrow=none;"` edge bent as a quarter-circle) or simply a line at an angle across the opening; simplest robust option is a thin rectangle for the door leaf plus a rounded/arc edge for the swing path.
- **Windows**: thin rectangle in a contrasting stroke (e.g. `strokeColor=#0000FF;fillColor=#ffffff;`) inset into the wall line.
- Label rooms with a transparent text-only cell (`style="text;html=1;align=center;"`) centered in each room polygon.
- Scale: pick a consistent px-per-unit (e.g. 1px = 1cm or 1 inch) and note it in a caption cell so proportions read correctly; bump `pageWidth`/`pageHeight` for a full building footprint rather than cramming into the default single-page bounds.

Other shape libraries exist for tech/cloud diagrams if needed (aws4, azure2, gcp2, kubernetes, cisco19, bpmn, flowchart, material_design, network, electrical, pid, rack, sitemap, and more) — ask if a specific icon set is needed; don't guess exact shape names for a library not covered here.

## Filled arbitrary shapes (rooms, custom outlines) — critical, easy to get wrong

For any closed shape that needs a solid fill and isn't a plain rectangle/ellipse (a room wedge, an irregular outline, a custom polygon), use a **vertex** with the `mxgraph.basic.polygon` stencil — NOT an edge with points and `fillColor`. mxGraph edges never render `fillColor` as an area fill regardless of `closed=1` or other flags; only a real vertex shape fills.

```xml
<mxCell value="" style="shape=mxgraph.basic.polygon;polyCoords=[[0.5,0.0],[1.0,0.35],[0.8,1.0],[0.2,1.0],[0.0,0.35]];fillColor=#b1dbb8;strokeColor=#000000;strokeWidth=2;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="200" height="180" as="geometry"/>
</mxCell>
```

`polyCoords` points are normalized 0–1 **within the cell's own bounding box** (the `mxGeometry` x/y/width/height), not absolute canvas coordinates. To place a real-world polygon: compute its absolute vertices, take the bounding box (min/max x and y), then normalize each point as `(x-minX)/width, (y-minY)/height`, and set the cell's geometry to that bounding box.

**Always verify by rendering, not just by XML-validating.** A file can be perfectly well-formed XML and still render as bare unfilled outlines if the fill technique is wrong — that failure is invisible to a schema/parser check. Before calling a diagram done: open a live app.diagrams.net session, use Extras → Edit Diagram to paste the generated `<mxGraphModel>` XML for a page, click Apply, and actually look at a screenshot. Don't skip this step for "it validated fine."

## Delivering

1. Write the file as `<name>.drawio` (plain XML, the extension is what makes draw.io/diagrams.net open it directly).
2. Tell the user where it landed and that it opens in app.diagrams.net (drag-and-drop or File → Open) or the desktop/VS Code draw.io extension.
3. If asked to iterate ("move X", "add a door here", "change this room's color"), edit specific `mxCell` elements by `id` rather than regenerating the whole file — find the id from the existing XML, then targeted-edit it.
