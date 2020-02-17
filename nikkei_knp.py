import neologdn
import re
import argparse
import os
import json
from tqdm import tqdm
import time
from pyknp import KNP
from contextlib import redirect_stdout

class RegexPattern:

    class Pattern:
        def __init__(self, ptn, *args):
            self.ptn = re.compile(ptn)
            self.g = args

        def group(self, i):
            return self.g[i]

    TITLE_0 = Pattern("[\(|（]?\d[\)|）|\.]\s?(?P<text>.+)", "text")
    TITLE_1 = Pattern("[①|②|③|④|⑤|⑥|⑦|⑧|⑨|⑩|○|■]")
    TITLE_2 = Pattern("[\s|\n][a-z][\.|．]")
    NUMBER = Pattern("\d+([,，]\d{3})*[千百十]?[兆億万]?")
    TICKER_CODE = Pattern(r"^\d{4}\.csv$")

knp = KNP()

NEOLOGD_PATH = "/usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd"
DIC_PATH = "/home/zaisan/Yuho/yuhoanalyze/config/mecab_dic/fintech.dic"

brackets_pair = re.compile('【[^】]*】$')
brackets_head = re.compile('^【[^】]*】')

input_directory = ""

output_directory = ""

def morphological_analysis(text: str):
    text = text.replace("\n", "")
    result = knp.parse(text)
    ret = []
    for mrph in result.mrph_list():
        ret.append(mrph.genkei)
    ret.append("\n")
    return ret

def remove_brackets(input):
    """先頭、末尾の隅付き括弧で囲まれた部分を除去
    """
    output = re.sub(brackets_head, '',
                    re.sub(brackets_pair, '', input))
    return output

def call_neologdn(input):
    output = neologdn.normalize(input)
    return output

def to_lowercase(input):
    output = input.lower()
    return output

def normalize_file(in_fname, out_fname):
    with open(in_fname, 'r') as rf, open(out_fname, 'w') as wf:
        df = json.load(rf)
        new_article = []
        new_abstract = []
        for line in df["article"]:
            n = call_neologdn(line)
            n = remove_brackets(n)
            n = to_lowercase(n)
            # 数字をNUMに
            n = RegexPattern.NUMBER.ptn.sub("NUM", n)
            #morph by KNP
            try:
                n = " ".join(morphological_analysis(n))
                if n == " " or n == "" or n == "\n":
                    continue
            except Exception as e:
                print(e)
            new_article.append(n)
        for line in df["abstract"]:
            n = call_neologdn(line)
            n = remove_brackets(n)
            n = to_lowercase(n)
            # 数字をNUMに
            n = RegexPattern.NUMBER.ptn.sub("NUM", n)
            #morph by KNP
            try:
                n = " ".join(morphological_analysis(n))
                if n == " " or n == "" or n == "\n":
                    continue
            except Exception as e:
                print(e)
            new_abstract.append(n)
        df["article"] = new_article
        df["abstract"] = new_abstract
        json.dump(df, wf, indent=4, ensure_ascii=False)
            

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-input', '--input_directory', dest='input', type=str, required=True)
    parser.add_argument('-ouput', '--output_directory', dest='output', type=str, required=True)
    args = parser.parse_args()

    input_directory = args.input
    output_directory = args.output
    if not os.path.exists(output_directory): os.makedirs(output_directory)
    sorted_input = sorted(os.listdir(input_directory))
    start = time.time()
    for f in sorted_input:
        input_path = os.path.join(input_directory, f)
        output_path = os.path.join(output_directory, f)
        normalize_file(input_path, output_path)
    elapsed_time = time.time()-start
    print(elapsed_time)

if __name__ == '__main__':
    main()