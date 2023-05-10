from enum import Enum

InsertStrategy = Enum("InsertStrategy", ["BULK", "SINGLE", "CHUNK_BISECT", "ADAPTIVE"])
