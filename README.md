<h1 align="center">
  <img src="md/font.png" alt="Coffee2Go" > 
</h1>

**Coffee2Go** is a very early-stage Python GUI tool that attempts to convert basic Java code into equivalent Go code.

⚠️ **Disclaimer:** This tool is **not fully functional** yet. It was created as an experimental idea and proof of concept, and many translations are either incomplete, incorrect, or overly simplified. **Manual review and editing is always required.**

---

## 🧠 Idea

The idea behind Coffee2Go is to build a lightweight, beginner-friendly tool that helps visualize and understand the differences between Java and Go syntax. It's primarily aimed at students, hobbyists, or anyone curious about how Java structures might look in Go.

Unlike advanced compilers or transpilers, this tool relies on simple string-based replacements and patterns — not a full parser or AST. Its purpose is more educational than practical.

The GUI is built with Python and Tkinter, so it can run on most systems without any extra dependencies.

---

## ✨ Features

- Load and parse `.java` files
- Basic Java-to-Go translation:
  - `System.out.print*` → `fmt.Print*`
  - Translating `if`, `for`, and `while` blocks
  - Primitive variable declarations
  - Java string methods like `.equals()`, `.length()`, `.substring()` get basic Go equivalents
  - Converts class names to Go `struct` definitions (simplified)
  - Optionally uppercase struct field names for export in Go
  - Replaces `try/catch` blocks with comments in Go, noting manual attention is needed
- Built-in code editor: view and modify input/output inside the app
- Save translated Go code to a `.go` file with one click
- Cross-platform (Python + Tkinter based)

---

## 📥 Input vs Output Example

> **Note:** The following is a simple illustration. Real output may require cleanup or fixing by hand.

### Java Input

```java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, Go world!");
    }
}
```

### Go Output
```go
package main

import (
    "fmt"
)

func main() {
    fmt.Println("Hello, Go world!")
}
```

## 🚀 How to Run

### Requirements
- Python 3.x
- Tkinter (usually included with standard Python installation)
- No external libraries required

### Launch the app

```bash
python main.py
```
This will open a simple GUI window with file selection, options, and a translation panel.

## ⚠️ Limitations

This tool is highly experimental and not intended for serious development use.

- ❌ No support for object-oriented features like inheritance, interfaces, or polymorphism
- ❌ No full parsing — relies entirely on regex and string replacements
- ❌ Complex Java constructs like anonymous classes, lambdas, enums, and streams are ignored
- ❌ Error handling, type checking, and proper code formatting are not implemented
- ❗ Output Go code may not compile or run without modification
- 🧪 Best suited for simple class examples or learning purposes

## 🧪 Status

This project is still in a prototype phase and mainly serves as an exploratory tool.
If you're expecting accurate translations for production-level Java code, this is not the right tool (yet 😉).

## 🤝 Contributions

This is a casual, open-ended learning project. Contributions are welcome — whether it's bug fixes, improved translation logic, or just suggestions.

Feel free to open an issue or pull request on GitHub.

## 📄 License

Licensed under the Apache License 2.0.
See the LICENSE file for full details.

