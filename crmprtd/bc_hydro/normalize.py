import sys

from dateutil import parser as date_parse
from sly import Lexer, Parser


class Empty(object):
    def __repr__(self):
        return "Empty"


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


class DataParser(Parser):
    tokens = DataLexer.tokens

    @_("station_name header_line data_lines")
    def extended_bch_csv(self, p):
        pass

    @_("header_line data_lines")
    def bch_csv(self, p):
        pass

    @_("WORD NEWLINE")
    def station_name(self, p):
        pass

    @_("header_names NEWLINE")
    def header_line(self, p):
        pass

    @_("header_name", "header_names header_name")
    def header_names(self, p):
        pass

    @_("WORD")
    def header_name(self, p):
        return p[0]

    @_("data_line", "data_lines data_line")
    def data_lines(self, p):
        pass

    @_("WORD DATE data_values NEWLINE", "NEWLINE")
    def data_line(self, p):
        return

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
            return Empty()
        return p[0]

    def error(self, t):
        import pdb

        pdb.set_trace()


if __name__ == "__main__":
    stream = open(sys.argv[1]).read()
    lexer = DataLexer()
    parser = DataParser()

    if sys.argv[2] == "parse":
        try:
            print(parser.parse(lexer.tokenize(stream)))
        except EOFError:
            pass

    else:
        for token in lexer.tokenize(stream):
            print(token)
