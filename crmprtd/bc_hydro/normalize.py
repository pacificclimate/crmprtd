import sys
from itertools import islice, chain

from dateutil import parser as date_parse
from sly import Lexer, Parser

from crmprtd import Row


def normalize(file_stream):
    lexer = DataLexer()
    parser = BCHydroExtendedCSV()
    tokens = lexer.tokenize(file_stream.read().decode("UTF-8"))
    yield from parser.parse(tokens)


class DataLexer(Lexer):
    tokens = {"DATE", "NUMBER", "NAN", "WORD", "NEWLINE"}

    NAN = r"\+"
    WORD = r"[ A-Za-z_/]+[A-Za-z]"
    NEWLINE = r"\n"

    ignore_whitespace = r"(\t|[\t ]{2,})"

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

    @_("extended_bch_csv", "extended_bch_csv extended_bch_csvs")
    def extended_bch_csvs(self, p):
        if hasattr(p, "extended_bch_csvs"):
            return chain([p.extended_bch_csv], p.extended_bch_csvs)
        return p.extended_bch_csv

    @_("station_name bch_csv", "bch_csv")
    def extended_bch_csv(self, p):
        return p.bch_csv

    @_("header_line data_lines NEWLINE")
    def bch_csv(self, p):
        def line_to_rows(header_line, data_line):
            dt = data_line["datetime"]
            station_id = data_line["station_id"]
            return [
                Row(
                    time=dt,
                    val=value,
                    variable_name=variable_name,
                    network_name="BCH",
                    station_id=station_id,
                    unit=None,
                    lat=None,
                    lon=None,
                )
                for variable_name, value in zip(header_line[2:], data_line["values"])
                if value is not None
            ]

        list_of_lists = [
            line_to_rows(p.header_line, data_line) for data_line in p.data_lines
        ]
        return chain.from_iterable(list_of_lists)

    @_("WORD NEWLINE")
    def station_name(self, p):
        """This is the station name in the header, but the station names are
        also listed in each data line. So we don't really care about
        this
        """
        pass

    @_("header_names NEWLINE")
    def header_line(self, p):
        return p.header_names

    @_("header_name", "header_names header_name")
    def header_names(self, p):
        if hasattr(p, "header_names"):
            return p.header_names + [p.header_name]
        else:
            return [p.header_name]

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

    @_("WORD DATE data_values NEWLINE")
    def data_line(self, p):
        if not hasattr(p, "WORD"):
            return

        return {"station_id": p.WORD, "datetime": p.DATE, "values": p.data_values}

    @_("data_value", "data_values data_value")
    def data_values(self, p):
        if len(p) == 1:
            return p.data_value
        else:
            if type(p.data_values) == list:
                return p.data_values + [p.data_value]
            return [p.data_values, p.data_value]

    @_("NUMBER", "NAN")
    def data_value(self, p):
        if p[0] == "+":
            return None
        return p[0]

    def error(self, t):
        if t is None:
            raise EOFError(
                "BCHydroExtendedCSV parser reached the end of the token stream. The file parsing has failed."
            )
        else:
            raise RuntimeError("Could not shift/merge token %s" % t)


if __name__ == "__main__":  # noqa
    if sys.argv[1] == "both":
        stream = open("AKI-hdq.txt").read() + open("CPI-hhq.txt").read()
    else:
        stream = open(sys.argv[1]).read()

    lexer = DataLexer()
    parser = BCHydroExtendedCSV()

    tokens = lexer.tokenize(stream)

    if sys.argv[2] == "parse":
        rows = parser.parse(tokens)

        for row in rows:
            print(row)

    else:
        for token in tokens:
            print(token)
