import sys
from docx import Document

def extract_requirements(doc_path):
    doc = Document(doc_path)
    requirements = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text and (text.lower().startswith("the system shall") or text.lower().startswith("the system must")):
            requirements.append(text)
    return requirements

def generate_test_code(requirements):
    test_code = [
        "import pytest",
        "",
        "# AUTO-GENERATED TEST CASES FROM SRS",
        ""
    ]
    
    for i, req in enumerate(requirements, 1):
        func_name = f"test_requirement_{i}"
        # A simple dummy test: just check requirement string is non-empty
        test_code.append(f"def {func_name}():")
        test_code.append(f"    # Requirement: {req}")
        test_code.append("    assert len('"+req+"') > 10  # example check")
        test_code.append("")
    return "\n".join(test_code)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python parse_srs.py <input_docx_path> <output_test_py_path>")
        sys.exit(1)

    input_doc = sys.argv[1]
    output_test = sys.argv[2]

    reqs = extract_requirements(input_doc)
    if not reqs:
        print("No requirements found in document.")
        sys.exit(1)

    code = generate_test_code(reqs)

    with open(output_test, "w") as f:
        f.write(code)

    print(f"Generated {len(reqs)} test cases in {output_test}")
