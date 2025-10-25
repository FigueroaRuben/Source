#!/usr/bin/env python3
import argparse
import json
import re
import sys

"""
Chicago Elections extractor (2024 presidential)
Usage examples:
    python "Chicago Elections.py" --url "https://www.politico.com/2024-election/results/illinois/"
    python "Chicago Elections.py" --file ./results.html --out results.json

This script does NOT contain any hard-coded election numbers.
It fetches/parses an HTML page or a local file and tries to extract vote totals
for the requested candidates (default: "Kamala Harris" and "Donald Trump").

Set --candidates to a comma-separated list if you need different name variants.
"""

# import optional third-party dependencies and provide a graceful fallback if BeautifulSoup is missing
try:
    import requests
except Exception:
    print("Missing dependency 'requests'. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)

# Try to import BeautifulSoup; if it's not installed, enable a lightweight fallback parser
try:
    from bs4 import BeautifulSoup  # type: ignore
    HAVE_BS4 = True
except Exception:
    from html import unescape
    HAVE_BS4 = False

def parse_text_from_html(html_text):
        # lightweight fallback: strip scripts/styles, remove tags and unescape entities
        text = re.sub(r"(?is)<script.*?>.*?</script>", " ", html_text)
        text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
        text = re.sub(r"(?s)<[^>]+>", " ", text)
        return unescape(text).strip()

def find_in_table(soup_or_html, name_regex):
        # look through table rows for candidate name and nearby numeric cells
        # If BeautifulSoup is available, use it; otherwise operate on raw HTML string
        if HAVE_BS4 and hasattr(soup_or_html, "find_all"):
                soup = soup_or_html
                for table in soup.find_all("table"):
                        for tr in table.find_all("tr"):
                                cells = [td.get_text(" ", strip=True) for td in tr.find_all(["td", "th"])]
                                row_text = " | ".join(cells)
                                if re.search(name_regex, row_text, flags=re.I):
                                        # prefer the first numeric token in the row that isn't part of the name
                                        nums = re.findall(r"[0-9][0-9,]*", row_text)
                                        if nums:
                                                return nums[0]
                return None
        else:
                html = soup_or_html
                # simple HTML-table parsing using regexes (sufficient for small, predictable pages)
                for table in re.findall(r"(?is)<table.*?>.*?</table>", html):
                        for tr in re.findall(r"(?is)<tr.*?>.*?</tr>", table):
                                cells = [re.sub(r"(?s)<[^>]+>", " ", c).strip() for c in re.findall(r"(?is)<t[dh].*?>(.*?)</t[dh]>", tr)]
                                row_text = " | ".join(cells)
                                if re.search(name_regex, row_text, flags=re.I):
                                        nums = re.findall(r"[0-9][0-9,]*", row_text)
                                        if nums:
                                                return nums[0]
                return None

def norm_int(s):
        # normalize numeric strings like "1,234" or None into integer or None
        if s is None:
                return None
        s = str(s).strip()
        if s == "":
                return None
        s = s.replace(",", "").replace(" ", "")
        try:
                return int(s)
        except Exception:
                return None

def extract_votes(html_text, candidates):
        # create either a BeautifulSoup object or use raw HTML + fallback parser
        if HAVE_BS4:
                soup = BeautifulSoup(html_text, "html.parser")
                page_text = soup.get_text("\n", strip=True)
        else:
                soup = html_text
                page_text = parse_text_from_html(html_text)

        results = {}
        for cand in candidates:
                name_regex = re.escape(cand)
                # try table search first
                num = find_in_table(soup, name_regex)
                if num is None:
                        num = find_in_text(page_text, name_regex)
                results[cand] = norm_int(num)
        return results


def find_in_text(text, name_regex):
        # look for "Name ... 1,234" or "1,234 ... Name"
        # pattern1: name then number within same line
        pat1 = re.compile(r"(" + name_regex + r").{0,80}?([0-9][0-9,]*)", flags=re.I)
        m = pat1.search(text)
        if m:
                return m.group(2)
        # pattern2: number then name
        pat2 = re.compile(r"([0-9][0-9,]*).{0,80}?(" + name_regex + r")", flags=re.I)
        m = pat2.search(text)
        if m:
                return m.group(1)
        return None




def main():
        p = argparse.ArgumentParser(description="Extract Chicago presidential vote totals from an HTML results page.")
        p.add_argument("--url", help="URL of the results page (HTML)")
        p.add_argument("--file", help="Local HTML file path")
        p.add_argument("--candidates", default="Kamala Harris,Donald Trump",
                                     help="Comma-separated candidate name variants to search for (default: Kamala Harris,Donald Trump)")
        p.add_argument("--out", help="Optional JSON output file")
        args = p.parse_args()

        if not args.url and not args.file:
                p.print_help()
                print("\nProvide --url or --file pointing to the official results page for Chicago/Cook County.", file=sys.stderr)
                sys.exit(1)

        if args.url:
                try:
                        r = requests.get(args.url, timeout=20)
                        r.raise_for_status()
                        html = r.text
                except Exception as e:
                        print("Failed to fetch URL:", e, file=sys.stderr)
                        sys.exit(1)
        else:
                try:
                        with open(args.file, "r", encoding="utf-8") as f:
                                html = f.read()
                except Exception as e:
                        print("Failed to read file:", e, file=sys.stderr)
                        sys.exit(1)

        candidates = [c.strip() for c in args.candidates.split(",") if c.strip()]
        results = extract_votes(html, candidates)

        out = {
                "source": args.url or args.file,
                "candidates": results,
        }

        json_text = json.dumps(out, indent=2)
        if args.out:
                with open(args.out, "w", encoding="utf-8") as f:
                        f.write(json_text)
                print("Saved results to", args.out)
        else:
                print(json_text)


if __name__ == "__main__":
        main()