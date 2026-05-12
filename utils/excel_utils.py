# -*- coding: utf-8 -*-
from pathlib import Path

import pandas as pd


excel_header_keywords_map = {
    "test_step_breakdown": ["项目", "功能域", "功能编号", "用例编号", "用例名称"]
}


def find_test_excel_header_idx(excel_path: Path, keyword_type: str):
    """通过关键字类型查找Excel表头序号"""
    return find_excel_header_idx(excel_path, excel_header_keywords_map[keyword_type])


def find_excel_header_idx(excel_path: Path, keywords: list):
    """通过关键字类型查找Excel表头序号"""
    df_preview = pd.read_excel(excel_path, header=None, nrows=10)
    for idx, row in df_preview.iterrows():
        row_text = " ".join(row.fillna("").astype(str).values)
        if all(keyword in row_text for keyword in keywords):
            return idx
    return None


if __name__ == "__main__":
    test_case_v3_path = Path("E:\\Workspaces\\Python\\test-step-generate\\data\\input\\test-case-v3-min.xlsx")
    print(find_test_excel_header_idx(test_case_v3_path, "test_step_breakdown"))
