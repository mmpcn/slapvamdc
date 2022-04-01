#!/usr/bin/python3
"""
This writes LaTeX for the rows of our table of LineTAP columns.  Technically,
this obtains the info from the standard columns of an operational (and
hopefully validated) table at dc.g-vo.org.

Dependency: python3-pyvo (and hence astropy).
"""

import pyvo

NON_NULL_COLUMNS = {'title', 'vacuum_wavelength', 'inchi', 'inchikey'}
TYPE_MAP = {
	("char", "*"): "text",
	("int", ""): "integer",
	("double", ""): "float",}


def e(tx):
	"""returns tx with TeX's standard active (and other magic) characters 
	escaped.
	"""
	return tx.replace("\\", "$\\backslash$"
		).replace("&", "\\&"
		).replace("#", "\\#"
		).replace("%", "\\%"
		).replace("_", "\\_"
		).replace("}", "\\}"
		).replace("{", "\\{"
		).replace('"', '{"}')


def get_type(datatype, arraysize, nonnull):
	"""returns a simple type identifier for a VOTable datatype/arraysize.

	Well, this really only nows what people have manually entered into
	TYPE_MAP above...
	"""
	res = e(TYPE_MAP[datatype, arraysize])
	if nonnull:
		res = f"\\textbf{{{res}}}"
	return res


def main():
	svc = pyvo.tap.TAPService("http://dc.g-vo.org/tap")
	rows = []

	for row in svc.run_sync("""
			select column_name, description, unit, ucd, datatype, arraysize
			from tap_schema.columns
			where 
  			table_name='toss.line_tap'
  			and std=1
			order by column_index"""):

		parts = [r"\texttt{{{}}}".format(e(row["column_name"]))]
		if row["unit"]:
			parts.append(e("["+row["unit"].replace("Angstrom", "Å")+"]"))
		parts.append(r"\hfil\break\ucd{{{}}}".format(e(row["ucd"])))
		
		parts.append("&")
		parts.append(get_type(
			row["datatype"], 
			row["arraysize"], 
			row["column_name"] in NON_NULL_COLUMNS))

		parts.append("&")
		parts.append(r"\raggedright "+e(row["description"]))

		rows.append(" ".join(parts)+r"\tabularnewline")
	
	print("\n\\rowsep\n".join(rows))


if __name__=="__main__":
	main()
