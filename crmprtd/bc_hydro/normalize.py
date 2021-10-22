import pdb
import sys
from itertools import islice, chain

from dateutil import parser as date_parse
from sly import Lexer, Parser

from crmprtd import Row


class DataLexer(Lexer):
    tokens = {"DATE", "NUMBER", "EMPTY", "WORD", "NEWLINE"}

    EMPTY = "\+"
    WORD = r"[ A-Za-z_/]+[A-Za-z]"
    NEWLINE = r"\n"

    ignore_whitespace = r"(\t|[\t ]{2,})"
    # ignore_newline = r"\n+"

    @_(r"[0-9]{4}[-/][0-9]{2}[-/][0-9]{2}( [0-9]{2}:[0-9]{2})?")
    def DATE(self, t):
        t.value = date_parse.parse(t.value)
        return t

    @_(r"-?\d+(\.\d+)?")
    def NUMBER(self, t):
        t.value = float(t.value)
        return t

    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1


class BCHydroExtendedCSV(Parser):
    tokens = DataLexer.tokens

    def __init__(self):
        self.variables = []

    @_("station_name bch_csv", "bch_csv")
    def extended_bch_csv(self, p):
        return p.bch_csv

    @_("header_line data_lines")
    def bch_csv(self, p):
        return chain.from_iterable(p.data_lines)

    @_("WORD NEWLINE")
    def station_name(self, p):
        """This is the station name in the header, but the station names are
        also listed in each data line. So we don't really care about
        this
        """
        pass

    @_("header_names NEWLINE")
    def header_line(self, p):
        pass

    @_("header_name", "header_names header_name")
    def header_names(self, p):
        self.variables.append(p.header_name)

    @_("WORD")
    def header_name(self, p):
        return p.WORD

    @_("data_line", "data_line data_lines")
    def data_lines(self, p):
        # According to this grammer, and empty NEWLINE is a valid data line
        # Trim this out if we see it.
        line = [p.data_line] if p.data_line else []

        if hasattr(p, "data_lines"):
            return line + p.data_lines
        else:
            return line

    @_("WORD DATE data_values NEWLINE", "NEWLINE")
    def data_line(self, p):
        if not hasattr(p, "WORD"):
            return

        station_id = p.WORD
        datetime = p.DATE
        rows = [
            Row(
                time=datetime,
                val=value,
                variable_name=variable_name,
                network_name="BCH",
                station_id=station_id,
                unit=None,
                lat=None,
                lon=None,
            )
            for variable_name, value in islice(
                zip(self.variables, p.data_values), 2, None
            )
            if value is not None
        ]
        return rows

    @_("data_value", "data_values data_value")
    def data_values(self, p):
        if len(p) == 1:
            return p.data_value
        else:
            if type(p.data_values) == list:
                return p.data_values + [p.data_value]
            return [p.data_values, p.data_value]

    @_("NUMBER", "EMPTY")
    def data_value(self, p):
        if p[0] == "+":
            return None
        return p[0]

    def error(self, t):
        import pdb

        pdb.set_trace()
        return


if __name__ == "__main__":
    stream = open(sys.argv[1]).read()
    lexer = DataLexer()
    parser = BCHydroExtendedCSV()

    tokens = lexer.tokenize(stream)

    if sys.argv[2] == "parse":
        try:
            try:
                rows = parser.parse(tokens)
            except Exception as e:
                pdb.set_trace()
            for row in rows:
                print(row)
        except EOFError:
            print("EOFERROR")

    else:
        for token in tokens:
            print(token)
