local function safe_ipairs(t)
  if type(t) == "table" then
    return ipairs(t)
  else
    return ipairs({})
  end
end

local function escape_latex(s)
  s = tostring(s or "")
  s = s:gsub("\\", "\\textbackslash{}")
  s = s:gsub("([{}%%$#&_])", "\\%1")
  s = s:gsub("%^", "\\^{}")
  s = s:gsub("~", "\\~{}")
  return s
end

local function blocks_to_text(blocks)
  if not blocks then
    return ""
  end
  return escape_latex(pandoc.utils.stringify(blocks):gsub("\n", " "))
end

local function cell_to_text(cell)
  if not cell then
    return ""
  end

  -- In aktuellen Pandoc-Versionen enthält eine Cell typischerweise .contents
  if cell.contents ~= nil then
    return blocks_to_text(cell.contents)
  end

  -- Fallback für ältere / anders aufgebaute Strukturen
  return escape_latex(pandoc.utils.stringify(cell):gsub("\n", " "))
end

local function alignment_to_latex(align)
  local a = tostring(align or "")
  if a:match("Right") then
    return "r"
  elseif a:match("Center") then
    return "c"
  else
    return "l"
  end
end

local function row_to_latex(row)
  local parts = {}

  if not row then
    return ""
  end

  for _, cell in safe_ipairs(row.cells) do
    table.insert(parts, cell_to_text(cell))
  end

  return table.concat(parts, " & ") .. " \\\\ \\hline"
end

function Table(tbl)
  -- Nur für LaTeX/PDF ausgeben, sonst Originaltabelle behalten
  if FORMAT ~= "latex" and FORMAT ~= "beamer" then
    return nil
  end

  local aligns = {}
  for _, colspec in safe_ipairs(tbl.colspecs) do
    local align = nil
    if type(colspec) == "table" then
      align = colspec[1]
    end
    table.insert(aligns, alignment_to_latex(align))
  end

  if #aligns == 0 then
    -- Fallback: Anzahl Spalten aus erster verfügbarer Zeile ermitteln
    local first_row = nil

    if tbl.head and tbl.head.rows and tbl.head.rows[1] then
      first_row = tbl.head.rows[1]
    else
      for _, body in safe_ipairs(tbl.bodies) do
        if body.body and body.body[1] then
          first_row = body.body[1]
          break
        end
      end
    end

    local ncols = 1
    if first_row and first_row.cells then
      ncols = math.max(1, #first_row.cells)
    end

    for _ = 1, ncols do
      table.insert(aligns, "l")
    end
  end

  local latex = {}
  local coldef = "|" .. table.concat(aligns, "|") .. "|"

  table.insert(latex, "\\begin{tabular}{" .. coldef .. "}")
  table.insert(latex, "\\hline")

  -- Tabellenkopf
  if tbl.head and tbl.head.rows then
    for _, row in safe_ipairs(tbl.head.rows) do
      table.insert(latex, row_to_latex(row))
    end
  end

  -- Tabellenkörper
  for _, body in safe_ipairs(tbl.bodies) do
    if body.head then
      for _, row in safe_ipairs(body.head) do
        table.insert(latex, row_to_latex(row))
      end
    end

    if body.body then
      for _, row in safe_ipairs(body.body) do
        table.insert(latex, row_to_latex(row))
      end
    end
  end

  -- Tabellenfuß
  if tbl.foot and tbl.foot.rows then
    for _, row in safe_ipairs(tbl.foot.rows) do
      table.insert(latex, row_to_latex(row))
    end
  end

  table.insert(latex, "\\end{tabular}")

  return pandoc.RawBlock("latex", table.concat(latex, "\n"))
end
