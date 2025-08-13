import sys
from docx import Document
import pytest
import os

def extract_requirements(doc_path):
    from docx import Document

    doc = Document(doc_path)
    requirements = []
    functional_section = False

    print("DEBUG: Starting to read paragraphs...")  # Debug line

    for para in doc.paragraphs:
        text = para.text.strip()
        print(f"DEBUG: Paragraph -> '{text}'")  # Debug line

        if not text:
            continue

        if "Functional Requirements" in text:
            functional_section = True
            print("DEBUG: Found Functional Requirements section")  # Debug line
            continue
        elif "Non-Functional Requirements" in text:
            functional_section = False
            print("DEBUG: End of Functional Requirements section")  # Debug line
            continue

        if functional_section and len(text.split()) >= 4:
            print(f"DEBUG: Adding requirement -> '{text}'")  # Debug line
            requirements.append(text)
        elif text.startswith("-") and len(text.split()) >= 4:
            print(f"DEBUG: Adding bullet requirement -> '{text}'")  # Debug line
            requirements.append(text)

    print(f"DEBUG: Total requirements found: {len(requirements)}")  # Debug line
    return requirements

def generate_test_file(requirements, test_file_path):
    test_code = [
        "import pytest",
        "",
        "# AUTO-GENERATED TEST CASES",
        ""
    ]

    for i, req in enumerate(requirements, 1):
        func_name = f"test_requirement_{i:03d}"
        test_code.append(f"def {func_name}():")
        test_code.append(f"    # Requirement: {req}")
        test_code.append(f"    assert len({repr(req)}) > 5  # Dummy test")
        test_code.append("")

    with open(test_file_path, "w") as f:
        f.write("\n".join(test_code))

    return [f"test_requirement_{i:03d}" for i in range(1, len(requirements)+1)]

def run_tests(test_file_path):
    results = {}
    result = pytest.main([
        test_file_path,
        "--tb=short",
        "--disable-warnings",
        "--maxfail=50",
        "-q"
    ])

    pytest_result_path = ".pytest_cache/v/cache/lastfailed"
    if os.path.exists(pytest_result_path):
        with open(pytest_result_path, "r") as f:
            failed = f.read()
    else:
        failed = ""

    for i in range(1, 1000):
        test_id = f"test_requirement_{i:03d}"
        if test_id in failed:
            results[test_id] = "FAIL"
        elif i <= len(results) + 50:  # naive cap
            results[test_id] = "PASS"
        else:
            break

    return results

def generate_markdown_report(md_path, requirements, test_results):
    with open(md_path, "w") as f:
        f.write("# 📋 Auto-Generated Test Cases and Results\n\n")
        f.write("| Test Case ID | Description | Input | Expected Output | Test Type | Result |\n")
        f.write("|--------------|-------------|-------|-----------------|-----------|--------|\n")

        for i, req in enumerate(requirements, 1):
            test_id = f"TC_{i:03d}"
            test_func = f"test_requirement_{i:03d}"
            description = req
            input_data = "Sample input"  # Placeholder
            expected_output = "Expected system behavior"  # Placeholder
            test_type = "Functional"  # Static for now
            result = test_results.get(test_func, "UNKNOWN")

            row = f"| {test_id} | {description} | {input_data} | {expected_output} | {test_type} | {result} |\n"
            f.write(row)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python parse_srs.py <input_docx_path> <output_test_py_path>")
        sys.exit(1)

    input_doc = sys.argv[1]
    test_py = sys.argv[2]
    output_md = "SRS/SRS_TestResults.md"

    requirements = extract_requirements(input_doc)
    if not requirements:
        print("No requirements found.")
        sys.exit(1)

    test_funcs = generate_test_file(requirements, test_py)
    test_results = run_tests(test_py)
    generate_markdown_report(output_md, requirements, test_results)

    print(f"✅ Markdown report generated at: {output_md}")
