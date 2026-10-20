import csv
import io
import operator

OPERATORS = {
    "==": operator.eq,
    "!=": operator.ne,
    "<": operator.lt,
    ">": operator.gt,
}


class Table:
    """用 CSV 文本初始化的内存表；所有单元格都按字符串存储和比较。"""

    def __init__(self, csv_text):
        rows = list(csv.reader(io.StringIO(csv_text)))
        if not rows or not rows[0]:
            raise ValueError("missing header")
        header = rows[0]
        if len(set(header)) != len(header):
            raise ValueError("duplicate column names")
        self.columns = header
        self.rows = []
        for row in rows[1:]:
            if len(row) != len(self.columns):
                raise ValueError(f"row width {len(row)} != {len(self.columns)}")
            self.insert(dict(zip(self.columns, row)))

    def insert(self, row):
        """插入一行；row 的列必须和表头完全一致，值必须是字符串。"""
        if set(row) != set(self.columns):
            raise ValueError("row columns must match the header")
        if not all(isinstance(value, str) for value in row.values()):
            raise ValueError("cell values must be str")
        self.rows.append(dict(row))

    def _check_column(self, column):
        if column not in self.columns:
            raise ValueError(f"unknown column: {column!r}")

    def query(self, columns, where=(), order=()):
        """where 是 AND 连接的 (column, op, value)；order 是 (column, descending) 列表，越靠前优先级越高。

        执行顺序：先筛选，再排序，最后投影，所以可以按不在 columns 里的列排序。
        """
        for column in columns:
            self._check_column(column)
        for column, op, _ in where:
            self._check_column(column)
            if op not in OPERATORS:
                raise ValueError(f"unsupported operator: {op!r}")
        for column, _ in order:
            self._check_column(column)

        matched = [
            row for row in self.rows
            if all(OPERATORS[op](row[column], value) for column, op, value in where)
        ]
        # Python 排序是稳定的：从优先级最低的键开始排，最后一次排序的键优先级最高
        for column, descending in reversed(order):
            matched.sort(key=lambda row: row[column], reverse=descending)
        return [{column: row[column] for column in columns} for row in matched]


def test():
    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__} should raise ValueError")

    # 字符串比较："10" < "2"，所以升序时 b 在前；排序列不在投影里也可以
    table = Table("name,score\na,2\nb,10\n")
    assert table.query(["name"], order=[("score", False)]) == [{"name": "b"}, {"name": "a"}]
    assert table.query(["name"], where=[("score", ">", "1")]) == [{"name": "a"}, {"name": "b"}]

    # 带引号的字段里可以有逗号
    table = Table('name,note\na,"x,y"\n')
    assert table.query(["note"]) == [{"note": "x,y"}]

    # 插入后可以按等值条件查到
    table.insert({"name": "b", "note": "z"})
    assert table.query(["name"], [("note", "==", "z")]) == [{"name": "b"}]

    # 多键排序：先按 team 升序，同队再按 name 降序
    table = Table("name,team\na,x\nb,y\nc,x\n")
    assert table.query(["name"], order=[("team", False), ("name", True)]) == [
        {"name": "c"},
        {"name": "a"},
        {"name": "b"},
    ]

    # 非法输入
    expect_value_error(Table, "a,a\n1,2\n")
    expect_value_error(Table, "a,b\n1\n")
    expect_value_error(table.insert, {"name": "d"})
    expect_value_error(table.query, ["missing"])
    expect_value_error(table.query, ["name"], [("team", "LIKE", "x")])


if __name__ == "__main__":
    test()
