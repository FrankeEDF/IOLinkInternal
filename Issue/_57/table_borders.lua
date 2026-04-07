local function latex_escape(s)
  s = tostring(s or "")
  s = s:gsub("\\", "\\textbackslash{}")
  s = s:gsub("([{}%%$#&_])", "\\%1")
  s = s:gsub("%^", "\\^{}")
  s = s:gsub("~", "\\~{}")
  return s
end

local function cell_text(cell)
  if not cell then
    return ""
  end

  -- Pandoc Cell -> contents (Blocks)
  if cell.contents then
    return latex_escape(pandoc.utils.stringify(cell.contents))
  end

  return ""
end

local function row_cells(row)
  local out = {}
  if not row or not row.cells then
    return out
  end

  for _, cell in ipairs(row.cells) do
    out[#out + 1] = cell_text(cell)
  end
  return out
end

local function collect_rows(tbl)
  local rows = {}

  -- Kopf
  if tbl.head and tbl.head.rows then
    for _, row in ipairs(tbl.head.rows) do
      rows[#rows + 1] = row
    end
  end

  -- Bodies
  if tbl.bodies then
    for _, body in ipairs(tbl.bodies) do
      if body.head then
        for _, row in ipairs(body.head) do
          rows[#rows + 1] = row
        end
      end
      if body.body then
        for _, row in ipairs(body.body) do
          rows[#rows + 1] = row
        end
      end
    end
  end

  -- Fuß
  if tbl.foot and tbl.foot.rows then
    for _, row in ipairs(tbl.foot.rows) do
      rows[#rows + 1] = row
    end
  end

  return rows
end

function Table(tbl)
  if FORMAT ~= "latex" and FORMAT ~= "beamer" then
    return nil
  end

  local rows = collect_rows(tbl)
  if #rows == 0 then
    return nil
  end

  -- Spaltenzahl aus echten Zellen bestimmen, nicht aus colspecs
  local ncols = 0
  for _, row in ipairs(rows) do
    if row.cells and #row.cells > ncols then
      ncols = #row.cells
    end
  end

  if ncols == 0 then
    return nil
  end

  local coldef_parts = {}
  for _ = 1, ncols do
    coldef_parts[#coldef_parts + 1] = "l"
  end
  local coldef = "|" .. table.concat(coldef_parts, "|") .. "|"

  local latex = {}
  latex[#latex + 1] = "\\begin{tabular}{" .. coldef .. "}"
  latex[#latex + 1] = "\\hline"

  for _, row in ipairs(rows) do
    local cells = row_cells(row)

    -- auf volle Spaltenzahl auffüllen
    while #cells < ncols do
      cells[#cells + 1] = ""
    end

    latex[#latex + 1] = table.concat(cells, " & ") .. " \\\\ \\hline"
  end

  latex[#latex + 1] = "\\end{tabular}"

  return pandoc.RawBlock("latex", table.concat(latex, "\n"))
end
