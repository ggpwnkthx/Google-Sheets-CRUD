import pandas as pd
import gspread
import string

class GoogleSpreadsheet:
    def __init__(self, credential: dict, spreadsheet: str, worksheet: str, has_header: bool = False, header: list = None):
        self.service_account = gspread.service_account_from_dict(credential)
        self.spreadsheet = self.service_account.open(spreadsheet)
        self.worksheet = self.spreadsheet.worksheet(worksheet)
        self.has_header = has_header
        if has_header:
            self.header = self.worksheet.row_values(1)
        else:
            self.header = []
            for i in range(0, len(self.worksheet.row_values(1))):
                self.header.append(self.__n2a(i))
        if header is not None:
            self.header = header

    def __n2a(self, n, b=string.ascii_uppercase):
        d, m = divmod(n, len(b))
        return self.__n2a(d-1, b)+b[m] if d else b[m]

    def __next_available_row(self):
        str_list = list(filter(None, self.worksheet.col_values(1)))
        return len(str_list)+1
    
    def __get_row_at_index(self, index):
        row = {}
        values = self.worksheet.row_values(index)
        for index, value in enumerate(self.header):
            row[value] = values[index]
        return row

    def create(self, rows: list):
        for row in rows:
            data = []
            for column in self.header:
                if column in row.keys():
                    data.append(row[column])
                else:
                    row[column] = None
                    data.append("")
            index = self.__next_available_row()
            row["index"] = index
            self.worksheet.insert_row(data, index)
        return pd.DataFrame(rows).set_index("index")

    def read(self, **kwargs):
        if self.has_header:
            df = pd.DataFrame(self.worksheet.get_all_records())
            df["index"] = df.apply(lambda x: x.name + 2, axis=1)
        else:
            df = pd.DataFrame(self.worksheet.get_all_values())
            df.columns = self.header
            df["index"] = df.apply(lambda x: x.name + 1, axis=1)

        filters = None
        for key, value in kwargs.items():
            condition = df[key] == value
            if filters is None:
                filters = condition
            else:
                filters = filters & condition
        if filters is not None:
            df = df[filters].dropna()
        return df.set_index("index")

    def update(self, rows):
        if isinstance(rows, pd.DataFrame):
            rows.reset_index(inplace=True)
            rows = rows.to_dict(orient="records")
        cells = []
        for new_row in rows:
            row_index = new_row["index"]
            old_row = self.__get_row_at_index(row_index)
            for key, value in new_row.items():
                if key != "index":
                    if value != old_row[key]:
                        column_index = self.header.index(key) + 1
                        cells.append(gspread.Cell(row=row_index, col=column_index, value=value))
        if len(cells):
            self.worksheet.update_cells(cells)

    def delete(self, row_index: int):
        self.worksheet.delete_rows(row_index)