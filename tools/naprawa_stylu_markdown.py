#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import shutil
from pathlib import Path

HEADER_RE = re.compile(r'^(#{1,6})\s+(.+)$')
CODEBLOCK_RE = re.compile(r'^```')

def analyze(lines):
    """
    Zwraca:
      - header_issues: błędy hierarchii nagłówków (skoki w górę > 1)
      - trailing_backslashes: linie z końcowym '\'
      - codeblock_issue: nieparzysta liczba bloków ```
    """
    header_issues = []
    trailing = []

    inside_code = False
    codeblock_count = 0
    prev_header_level = None
    prev_header_line = None

    for idx, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")

        # blok kodu
        if CODEBLOCK_RE.match(line):
            inside_code = not inside_code
            codeblock_count += 1
            continue

        if inside_code:
            continue

        # nagłówki
        m = HEADER_RE.match(line)
        if m:
            level = len(m.group(1))

            if prev_header_level is not None:
                delta = level - prev_header_level
                if delta > 1:
                    header_issues.append({
                        "line": idx,
                        "line_text": line,
                        "prev_line": prev_header_line,
                        "prev_level": prev_header_level,
                        "curr_level": level,
                        "delta": delta
                    })

            prev_header_level = level
            prev_header_line = idx
            continue

        # końcowy '\'
        if line.endswith("\\") and line.strip() != "\\":
            trailing.append({"line": idx, "line_text": line})

    codeblock_issue = (codeblock_count % 2 != 0)
    return header_issues, trailing, codeblock_issue


def extract_headers(lines):
    headers = []
    inside_code = False

    for idx, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")

        if CODEBLOCK_RE.match(line):
            inside_code = not inside_code
            continue

        if inside_code:
            continue

        m = HEADER_RE.match(line)
        if m:
            headers.append({
                "line": idx,
                "level": len(m.group(1)),
                "text": m.group(2)
            })

    return headers


def print_headers_tree(headers):
    print("\n--- Struktura nagłówków ---")
    for h in headers:
        indent = "  " * (h["level"] - 1)
        print(f"{indent}- (linia {h['line']}) {h['text']}")
    print("--- Koniec struktury ---\n")


def apply_fixes(lines):
    new_lines = []
    inside_code = False
    prev_header_level = None

    for idx, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")

        # blok kodu
        if CODEBLOCK_RE.match(line):
            inside_code = not inside_code
            new_lines.append(raw)
            continue

        if inside_code:
            new_lines.append(raw)
            continue

        # naprawa nagłówków
        m = HEADER_RE.match(line)
        if m:
            hashes = m.group(1)
            text = m.group(2)
            level = len(hashes)

            if prev_header_level is not None and level > prev_header_level + 1:
                level = prev_header_level + 1
                hashes = "#" * level
                line = f"{hashes} {text}"

            prev_header_level = level

        # naprawa końcowego '\'
        if line.endswith("\\") and line.strip() != "\\":
            line = line[:-1]

        # ZAWSZE zapisujemy poprawioną linię
        new_lines.append(line + "\n")

    return new_lines



def print_report(header_issues, trailing, codeblock_issue):
    if not header_issues and not trailing and not codeblock_issue:
        print("Brak wykrytych problemów.")
        return

    if header_issues:
        print("\nProblemy z hierarchią nagłówków (skoki w górę > 1):")
        for it in header_issues:
            print(f"  - Linia {it['line']}: \"{it['line_text']}\"")
            print(f"    Poprzedni nagłówek: linia {it['prev_line']} poziom {it['prev_level']}, "
                  f"obecny poziom {it['curr_level']} (delta {it['delta']})")

    if trailing:
        print("\nLinie kończące się '\\' do poprawy:")
        for t in trailing:
            print(f"  - Linia {t['line']}: \"{t['line_text']}\"")

    if codeblock_issue:
        print("\n⚠️ UWAGA: Nieparzysta liczba bloków ``` — dokument może być uszkodzony!")


def prompt_choice():
    print("\nCo chcesz zrobić?")
    print("  1) Napraw i nadpisz plik (zrobię kopię .bak)")
    print("     - Naprawia hierarchię nagłówków (zmniejsza skoki >1 poziomu)")
    print("     - Usuwa niechciane końcowe backslashe '\\' na końcach linii")
    print("     - Wykrywa nieparzystą liczbę bloków kodu ``` (tylko ostrzega)")
    print("  2) Napraw i zapisz do nowego pliku")
    print("     - Jak powyżej, bez kopii pliku.")
    print("  3) Pokaż podgląd zmian (pierwsze 20 linii)")
    print("     - Pokazuje różnice między oryginalnym a naprawionym plikiem")
    print("  4) Pokaż strukturę nagłówków")
    print("     - Wyświetla drzewo nagłówków z poziomami")
    print("  5) Anuluj")

    mapping = {
        "1": "overwrite",
        "2": "newfile",
        "3": "preview",
        "4": "headers",
        "5": "abort",
    }

    return mapping.get(input("Wybór: ").strip())


def show_preview(old, new, max_lines=20):
    print("\n--- Podgląd zmian ---")
    for i in range(min(max_lines, max(len(old), len(new)))):
        old_line = old[i].rstrip("\n") if i < len(old) else ""
        new_line = new[i].rstrip("\n") if i < len(new) else ""
        if old_line != new_line:
            print(f"{i+1:4d}: - {old_line}")
            print(f"{i+1:4d}: + {new_line}")
    print("--- Koniec podglądu ---\n")


def main():
    path_str = input("Podaj ścieżkę do pliku .md (Markdown): \n(żadne zmiany nie będą jeszcze wprowadzone)").strip().strip('"')
    p = Path(path_str)

    if not p.exists():
        print("Plik nie istnieje.")
        input("Naciśnij klawisz aby zakończyć...")
        return

    lines = p.read_text(encoding="utf-8").splitlines(keepends=True)

    header_issues, trailing, codeblock_issue = analyze(lines)
    headers = extract_headers(lines)

    print_report(header_issues, trailing, codeblock_issue)

    fixed_lines = apply_fixes(lines)

    while True:
        action = prompt_choice()

        if action == "preview":
            show_preview(lines, fixed_lines)
            continue

        if action == "headers":
            print_headers_tree(headers)
            continue

        if action == "abort":
            print("Anulowano.")
            input("Naciśnij klawisz aby zakończyć...")
            return

        backup = p.with_suffix(p.suffix + ".bak")
        shutil.copy2(p, backup)
        print(f"Utworzono kopię zapasową: {backup}")

        if action == "overwrite":
            p.write_text("".join(fixed_lines), encoding="utf-8")
            print(f"Zapisano zmiany w pliku: {p}")
            break

        if action == "newfile":
            out = p.with_name(p.stem + "_fixed" + p.suffix)
            out.write_text("".join(fixed_lines), encoding="utf-8")
            print(f"Zapisano do nowego pliku: {out}")
            break

        print("Nieprawidłowy wybór.")

    input("Naciśnij klawisz aby zakończyć...")


if __name__ == "__main__":
    main()
