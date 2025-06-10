import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, ttk
import re
import os

class JavaToGoTranslator:
    def __init__(self):
        # Initialize the main window
        self.root = tk.Tk()
        self.root.title("Java to Golang Translator")
        self.root.geometry("1000x700")
        
        # Set up the main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the menu bar
        self.create_menu()
        
        # Create UI elements
        self.create_ui()
        
        # Add example templates
        self.setup_example_templates()
        
        # Translation rules mapping Java concepts to Go
        self.translation_rules = {
            # Java -> Go declarations
            r'public class (\w+)': r'package main\n\n// \1 represents the Java class \1\ntype \1 struct {',
            r'private (\w+) (\w+);': r'\2 \1 // private',
            r'public (\w+) (\w+);': r'\2 \1 // public',
            r'protected (\w+) (\w+);': r'\2 \1 // protected',
            r'(public|private|protected)? ?static void main\(String\[\] args\)': r'func main()',
            
            # Function declarations
            r'public (\w+) (\w+)\((.*?)\)': r'// \2 is the Go equivalent of the Java method\nfunc (\*this) \2(\3) \1',
            r'private (\w+) (\w+)\((.*?)\)': r'// \2 is the Go equivalent of the Java private method\nfunc (\*this) \2(\3) \1',
            
            # Control structures
            r'if \((.*?)\) \{': r'if \1 {',
            r'else \{': r'else {',
            r'for \((\w+) (\w+) = (\w+); \2 ([<>=!]+) (\w+); \2([\+\-]{2}|[\+\-]=\d+)\) \{': 
                r'for \2 := \3; \2 \4 \5; \2\6 {',
            r'while \((.*?)\) \{': r'for \1 {',
            r'do \{': r'for {',
            r'\} while\((.*?)\);': r'if !(\1) {\n    break\n}',
            
            # Variable declarations
            r'(\w+) (\w+) = (.*?);': r'\2 := \3 // \1',
            
            # Common Java methods to Go
            r'System\.out\.println\((.*?)\);': r'fmt.Println(\1)',
            r'System\.out\.print\((.*?)\);': r'fmt.Print(\1)',
            
            # Imports conversion
            r'import java\.util\..*;': r'import (\n    "fmt"\n    "time"\n    "strconv"\n    "strings"\n)',
            r'import java\.io\..*;': r'import (\n    "io"\n    "os"\n    "bufio"\n)',
            
            # Error handling
            r'try \{': r'// Go uses error handling instead of try-catch\n',
            r'\} catch\((.*?)\) \{': r'// Error handling for \1\nif err != nil {',
            r'throw new (\w+)\((.*?)\);': r'return fmt.Errorf("\1: %v", \2)',
            
            # Cleanup
            r'\}(\s*)\}': r'}\n}',
            r';\s*\n': '\n',
            r'}': '}',
        }
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Java File", command=self.open_file)
        file_menu.add_command(label="Save Go File", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="How to Use", command=self.show_help)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_ui(self):
        # Create top frame for input
        top_frame = ttk.LabelFrame(self.main_frame, text="Java Code Input", padding="10")
        top_frame.pack(fill=tk.BOTH, expand=True)
        
        # Template selection frame
        template_frame = ttk.Frame(top_frame)
        template_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(template_frame, text="Templates:").pack(side=tk.LEFT, padx=5)
        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(template_frame, textvariable=self.template_var, state="readonly", width=30)
        self.template_combo['values'] = ("Empty", "Hello World", "Simple Class", "For Loop Example", "Method Example")
        self.template_combo.current(0)
        self.template_combo.pack(side=tk.LEFT, padx=5)
        load_template_btn = ttk.Button(template_frame, text="Load Template", command=self.load_template)
        load_template_btn.pack(side=tk.LEFT, padx=5)
        
        # Options frame
        options_frame = ttk.Frame(top_frame)
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add translation options
        self.keep_comments_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Keep comments", variable=self.keep_comments_var).pack(side=tk.LEFT, padx=5)
        
        self.use_pointers_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Use pointers for structs", variable=self.use_pointers_var).pack(side=tk.LEFT, padx=5)
        
        self.capitalize_fields_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Capitalize exported fields", variable=self.capitalize_fields_var).pack(side=tk.LEFT, padx=5)
        
        # Java input text area
        self.java_text = scrolledtext.ScrolledText(top_frame, wrap=tk.WORD, width=80, height=15)
        self.java_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Middle frame for buttons
        middle_frame = ttk.Frame(self.main_frame, padding="10")
        middle_frame.pack(fill=tk.X)
        
        # Translate button
        translate_button = ttk.Button(middle_frame, text="Translate to Go", command=self.translate_code)
        translate_button.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        clear_button = ttk.Button(middle_frame, text="Clear Both", command=self.clear_text)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Copy button for Go code
        copy_button = ttk.Button(middle_frame, text="Copy Go Code", command=self.copy_go_code)
        copy_button.pack(side=tk.LEFT, padx=5)
        
        # Format button for Go code
        format_button = ttk.Button(middle_frame, text="Format Go Code", command=self.format_go_code)
        format_button.pack(side=tk.LEFT, padx=5)
        
        # Bottom frame for output
        bottom_frame = ttk.LabelFrame(self.main_frame, text="Generated Go Code", padding="10")
        bottom_frame.pack(fill=tk.BOTH, expand=True)
        
        # Go output text area
        self.go_text = scrolledtext.ScrolledText(bottom_frame, wrap=tk.WORD, width=80, height=15)
        self.go_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def format_go_code(self):
        """Apply basic formatting to Go code to make it more readable"""
        go_code = self.go_text.get("1.0", tk.END).strip()
        if not go_code:
            messagebox.showinfo("Info", "No Go code to format!")
            return
            
        try:
            # Simple indentation logic
            formatted_code = ""
            indent_level = 0
            lines = go_code.split('\n')
            
            for line in lines:
                stripped_line = line.strip()
                
                # Adjust indent level based on braces
                if stripped_line.endswith('{'):
                    formatted_code += '\t' * indent_level + stripped_line + '\n'
                    indent_level += 1
                elif stripped_line.startswith('}'):
                    indent_level = max(0, indent_level - 1)  # Prevent negative indent
                    formatted_code += '\t' * indent_level + stripped_line + '\n'
                elif stripped_line:  # Skip empty lines for indent calculation
                    formatted_code += '\t' * indent_level + stripped_line + '\n'
                else:
                    formatted_code += '\n'  # Preserve empty lines
            
            # Update the Go code text area
            self.go_text.delete("1.0", tk.END)
            self.go_text.insert("1.0", formatted_code)
            self.status_var.set("Go code formatted")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error formatting Go code: {str(e)}")
            self.status_var.set("Format error")
    
    def copy_go_code(self):
        """Copy the generated Go code to clipboard"""
        go_code = self.go_text.get("1.0", tk.END).strip()
        if go_code:
            self.root.clipboard_clear()
            self.root.clipboard_append(go_code)
            self.status_var.set("Go code copied to clipboard")
        else:
            messagebox.showinfo("Info", "No Go code to copy!")
            
    def setup_example_templates(self):
        """Create example Java code templates"""
        self.templates = {
            "Empty": "",
            "Hello World": """public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, Go world!");
    }
}""",
            "Simple Class": """public class Person {
    private String name;
    private int age;
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    public String getName() {
        return name;
    }
    
    public int getAge() {
        return age;
    }
    
    public void greet() {
        System.out.println("Hello, my name is " + name);
    }
}""",
            "For Loop Example": """public class LoopExample {
    public static void main(String[] args) {
        // Simple for loop
        for (int i = 0; i < 10; i++) {
            System.out.println("Count: " + i);
        }
        
        // While loop
        int j = 0;
        while (j < 5) {
            System.out.println("While: " + j);
            j++;
        }
    }
}""",
            "Method Example": """public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
    
    public int subtract(int a, int b) {
        return a - b;
    }
    
    public double divide(int a, int b) {
        if (b == 0) {
            throw new ArithmeticException("Cannot divide by zero");
        }
        return (double) a / b;
    }
    
    public static void main(String[] args) {
        Calculator calc = new Calculator();
        System.out.println("5 + 3 = " + calc.add(5, 3));
        System.out.println("10 - 4 = " + calc.subtract(10, 4));
        System.out.println("15 / 2 = " + calc.divide(15, 2));
    }
}"""
        }
    
    def load_template(self):
        """Load selected template into the Java text area"""
        template_name = self.template_var.get()
        if template_name in self.templates:
            # Clear existing text
            self.java_text.delete("1.0", tk.END)
            # Insert template
            self.java_text.insert("1.0", self.templates[template_name])
            self.status_var.set(f"Loaded {template_name} template")
    
    def translate_code(self):
        java_code = self.java_text.get("1.0", tk.END)
        if not java_code.strip():
            messagebox.showwarning("Warning", "Please enter Java code first!")
            return
        
        self.status_var.set("Translating...")
        self.root.update_idletasks()
        
        try:
            # Start with clean Go structure
            go_code = "package main\n\n"
            
            # Check for imports we'll likely need
            imports = []
            if "System.out" in java_code:
                imports.append("fmt")
            if "String" in java_code and ("toLowerCase" in java_code or "toUpperCase" in java_code or "substring" in java_code):
                imports.append("strings")
            if "Integer.parseInt" in java_code or "Double.parseDouble" in java_code:
                imports.append("strconv")
            
            # Add imports if needed
            if imports:
                go_code += 'import (\n'
                for imp in imports:
                    go_code += f'    "{imp}"\n'
                go_code += ')\n\n'
            
            # Check if this is a simple program with main method only
            main_method_match = re.search(
                r'public\s+static\s+void\s+main\s*\(\s*String\s*\[\]\s*\w+\s*\)\s*\{([\s\S]*?)(?=\s*\}\s*(?:\}|$))', 
                java_code
            )
            
            # Check for class definition
            class_match = re.search(r'public\s+class\s+(\w+)', java_code)
            class_name = class_match.group(1) if class_match else None
            
            # Check for class fields
            fields = []
            if class_name:
                field_pattern = r'(private|public|protected)?\s+(\w+)\s+(\w+)(?:\s*=\s*(.*?))?;'
                field_matches = re.finditer(field_pattern, java_code)
                for match in field_matches:
                    modifier, field_type, field_name, default_value = match.groups()
                    # Skip static fields and fields in methods
                    if "static" not in java_code[match.start()-10:match.start()] and self.is_outside_method(java_code, match.start()):
                        fields.append((field_type, field_name, default_value))
            
            # Check for methods
            methods = []
            if class_name:
                method_pattern = r'(public|private|protected)?\s+(?:static\s+)?(\w+)\s+(\w+)\s*\((.*?)\)\s*(?:throws\s+\w+(?:\.\w+)*)?\s*\{([\s\S]*?)(?=\s*\}\s*(?:\}|$|\w))'
                method_matches = re.finditer(method_pattern, java_code)
                for match in method_matches:
                    modifier, return_type, method_name, params, body = match.groups()
                    if method_name != "main":  # Skip main method as it's handled differently
                        methods.append((modifier, return_type, method_name, params, body))
            
            # Handle structs if needed
            if class_name and fields:
                go_code += f"// {class_name} represents the equivalent of Java class {class_name}\n"
                go_code += f"type {class_name} struct {{\n"
                for field_type, field_name, _ in fields:
                    go_type = self.java_to_go_type(field_type)
                    go_code += f"    {self.capitalize_field(field_name)} {go_type} // was {field_type}\n"
                go_code += "}\n\n"
                
                # Add constructor method (New function)
                if fields:
                    go_code += f"// New{class_name} creates a new {class_name} instance\n"
                    go_code += f"func New{class_name}("
                    
                    # Add parameters
                    param_parts = []
                    for field_type, field_name, _ in fields:
                        go_type = self.java_to_go_type(field_type)
                        param_parts.append(f"{field_name} {go_type}")
                    
                    go_code += ", ".join(param_parts)
                    go_code += f") *{class_name} {{\n"
                    go_code += f"    return &{class_name}{{\n"
                    
                    # Add field initializations
                    for field_type, field_name, _ in fields:
                        go_code += f"        {self.capitalize_field(field_name)}: {field_name},\n"
                    
                    go_code += "    }\n"
                    go_code += "}\n\n"
                
                # Add methods 
                for modifier, return_type, method_name, params, body in methods:
                    go_return_type = self.java_to_go_type(return_type)
                    
                    # Convert parameters to Go style
                    go_params = ""
                    if params.strip():
                        param_parts = []
                        for param in params.split(","):
                            param = param.strip()
                            if param:
                                param_parts_split = param.split()
                                if len(param_parts_split) >= 2:
                                    param_type, param_name = param_parts_split[0], param_parts_split[1]
                                    param_parts.append(f"{param_name} {self.java_to_go_type(param_type)}")
                        go_params = ", ".join(param_parts)
                    
                    # Convert method body
                    go_body = body
                    
                    # Replace this.field with s.Field
                    for _, field_name, _ in fields:
                        go_body = re.sub(r'this\.' + field_name, f"s.{self.capitalize_field(field_name)}", go_body)
                    
                    # Replace other Java-isms
                    go_body = self.convert_java_body_to_go(go_body)
                    
                    # Add method
                    go_code += f"// {method_name} is the Go equivalent of the Java method\n"
                    if go_return_type != "":
                        go_code += f"func (s *{class_name}) {method_name}({go_params}) {go_return_type} {{\n"
                    else:
                        go_code += f"func (s *{class_name}) {method_name}({go_params}) {{\n"
                    
                    # Add method body with indentation
                    for line in go_body.strip().split("\n"):
                        if line.strip():
                            go_code += f"    {line.strip()}\n"
                    
                    go_code += "}\n\n"
            
            # Handle main method if it exists
            if main_method_match:
                # Extract the body of the main method
                main_body = main_method_match.group(1).strip()
                
                # Translate the main body
                main_body = self.convert_java_body_to_go(main_body)
                
                # Create the main function in Go
                go_code += "func main() {\n"
                
                # Add each line of the translated body with proper indentation
                for line in main_body.split('\n'):
                    if line.strip():  # Skip empty lines
                        go_code += f"    {line.strip()}\n"
                
                go_code += "}\n"
            elif class_name and not main_method_match:
                # If there's a class but no main, add a simple main that creates and uses the class
                if fields and methods:
                    go_code += "func main() {\n"
                    go_code += f"    // Example of creating and using a {class_name} instance\n"
                    go_code += f"    // Uncomment and modify as needed\n"
                    go_code += f"    // instance := New{class_name}("
                    
                    # Add sample values for constructor
                    sample_values = []
                    for field_type, _, _ in fields:
                        sample_values.append(self.get_sample_value(field_type))
                    
                    go_code += ", ".join(sample_values)
                    go_code += ")\n"
                    
                    # Add a example method call if methods exist
                    if methods:
                        method = methods[0]
                        method_name = method[2]
                        go_code += f"    // instance.{method_name}()\n"
                    
                    go_code += "}\n"
            
            # Final output
            self.go_text.delete("1.0", tk.END)
            self.go_text.insert("1.0", go_code)
            self.status_var.set("Translation complete")
            
        except Exception as e:
            self.status_var.set("Translation error")
            messagebox.showerror("Error", f"An error occurred during translation: {str(e)}")
    
    def is_outside_method(self, code, position):
        """Check if the given position is outside any method body"""
        # Count open and close braces before position
        open_braces = 0
        in_string = False
        in_comment = False
        
        for i in range(position):
            if code[i] == '"' and (i == 0 or code[i-1] != '\\'):
                in_string = not in_string
            elif code[i:i+2] == '//' and not in_string:
                # Skip to end of line
                newline_pos = code.find('\n', i)
                if newline_pos == -1:
                    break
                i = newline_pos
            elif code[i:i+2] == '/*' and not in_string:
                in_comment = True
            elif code[i:i+2] == '*/' and in_comment:
                in_comment = False
                i += 1  # Skip the next character
            elif code[i] == '{' and not in_string and not in_comment:
                open_braces += 1
            elif code[i] == '}' and not in_string and not in_comment:
                open_braces -= 1
        
        # If we're at brace level 1, we're inside the class but outside methods
        return open_braces == 1
    
    def java_to_go_type(self, java_type):
        """Convert Java type to Go type"""
        type_map = {
            "int": "int",
            "long": "int64",
            "float": "float32",
            "double": "float64",
            "boolean": "bool",
            "String": "string",
            "char": "rune",
            "byte": "byte",
            "short": "int16",
            "void": "",
            "Object": "interface{}",
            "Integer": "int",
            "Double": "float64",
            "Boolean": "bool",
            "Character": "rune"
        }
        
        return type_map.get(java_type, java_type)
    
    def capitalize_field(self, field_name):
        """Capitalize the first letter of a field name for Go exported fields"""
        if not field_name:
            return field_name
        
        # Only capitalize if the option is checked
        if self.capitalize_fields_var.get():
            return field_name[0].upper() + field_name[1:]
        return field_name
    
    def get_sample_value(self, java_type):
        """Return a sample value for the given Java type"""
        type_samples = {
            "int": "0",
            "long": "0",
            "float": "0.0",
            "double": "0.0",
            "boolean": "false",
            "String": '""',
            "char": "'a'",
            "byte": "0",
            "short": "0",
            "Integer": "0",
            "Double": "0.0",
            "Boolean": "false"
        }
        
        return type_samples.get(java_type, "nil")
    
    def convert_java_body_to_go(self, java_body):
        """Convert Java code body to Go"""
        go_body = java_body
        
        # System.out conversions
        go_body = re.sub(r'System\.out\.println\((.*?)\);', r'fmt.Println(\1)', go_body)
        go_body = re.sub(r'System\.out\.print\((.*?)\);', r'fmt.Print(\1)', go_body)
        go_body = re.sub(r'System\.out\.printf\((.*?)\);', r'fmt.Printf(\1)', go_body)
        
        # String concatenation with + to fmt.Sprintf
        go_body = re.sub(r'(".*?")\s*\+\s*([\w\.]+)', r'fmt.Sprintf("%s%v", \1, \2)', go_body)
        go_body = re.sub(r'([\w\.]+)\s*\+\s*(".*?")', r'fmt.Sprintf("%v%s", \1, \2)', go_body)
        
        # Variable declarations
        go_body = re.sub(r'(\w+)\s+(\w+)\s*=\s*(.*?);', r'\2 := \3', go_body)
        
        # Method calls on objects
        go_body = re.sub(r'(\w+)\.(\w+)\((.*?)\);', r'\1.\2(\3)', go_body)
        
        # Control structures
        go_body = re.sub(r'if\s*\((.*?)\)\s*\{', r'if \1 {', go_body)
        go_body = re.sub(r'while\s*\((.*?)\)\s*\{', r'for \1 {', go_body)
        go_body = re.sub(r'for\s*\((\w+)\s+(\w+)\s*=\s*(\w+);\s*(\w+)\s*([<>=!]+)\s*(\w+);\s*(\w+)(\+\+|\-\-|\+=1|\-=1)\)\s*\{', 
                         r'for \2 := \3; \4 \5 \6; \7\8 {', go_body)
        
        # Return statements
        go_body = re.sub(r'return\s+(.*?);', r'return \1', go_body)
        
        # New object creation
        go_body = re.sub(r'new\s+(\w+)\((.*?)\)', r'\1{\2}', go_body)
        go_body = re.sub(r'(\w+)\s+(\w+)\s*=\s*new\s+(\w+)\((.*?)\);', r'\2 := &\3{\4}', go_body)
        
        # Remove semicolons
        go_body = re.sub(r';', '', go_body)
        
        return go_body
    
    def cleanup_code(self, code):
        """Clean up the translated code to make it more idiomatic Go"""
        # Remove extra semicolons (Go doesn't need them)
        code = re.sub(r';', '', code)
        
        # Fix braces formatting
        code = re.sub(r'\}\s*else', '} else', code)
        
        # Fix System.out.println that might have been missed
        code = re.sub(r'System\.out\.println\((.*?)\)', r'fmt.Println(\1)', code)
        code = re.sub(r'System\.out\.print\((.*?)\)', r'fmt.Print(\1)', code)
        code = re.sub(r'System\.out\.printf\((.*?)\)', r'fmt.Printf(\1)', code)
        
        # Replace Java specific String operations
        code = re.sub(r'([\w\.]+)\.equals\((.*?)\)', r'\1 == \2', code)
        code = re.sub(r'([\w\.]+)\.length\(\)', r'len(\1)', code)
        code = re.sub(r'([\w\.]+)\.charAt\((\d+)\)', r'\1[\2]', code)
        code = re.sub(r'([\w\.]+)\.toLowerCase\(\)', r'strings.ToLower(\1)', code)
        code = re.sub(r'([\w\.]+)\.toUpperCase\(\)', r'strings.ToUpper(\1)', code)
        code = re.sub(r'([\w\.]+)\.substring\((\d+),\s*(\d+)\)', r'\1[\2:\3]', code)
        code = re.sub(r'([\w\.]+)\.substring\((\d+)\)', r'\1[\2:]', code)
        
        # Fix variable declarations with types
        code = re.sub(r'(\w+)\s+(\w+)\s*=', r'\2 :=', code)
        
        # Fix for loops
        code = re.sub(r'for\s*\((\w+)\s+(\w+)\s*=\s*(\w+);\s*(\w+)\s*([<>=!]+)\s*(\w+);\s*(\w+)(\+\+|\-\-|\+=1|\-=1)\)', 
                      r'for \2 := \3; \4 \5 \6; \7\8', code)
        
        # Convert common conversions
        code = re.sub(r'Integer\.parseInt\((.*?)\)', r'strconv.Atoi(\1)', code)
        code = re.sub(r'Double\.parseDouble\((.*?)\)', r'strconv.ParseFloat(\1, 64)', code)
        code = re.sub(r'Boolean\.parseBoolean\((.*?)\)', r'strconv.ParseBool(\1)', code)
        
        # Exception handling
        code = re.sub(r'try\s*\{([\s\S]*?)\}\s*catch\s*\((.*?)\)\s*\{([\s\S]*?)\}', 
                      r'// Error handling in Go style\n\1\nif err != nil {\n\3\n}', code)
        
        # Fix comments
        code = re.sub(r'//(.*?)$', r'// \1', code, flags=re.MULTILINE)
        
        # Cleanup empty braces
        code = re.sub(r'\{\s*\}', r'{\n}', code)
        
        return code
    
    def open_file(self):
        """Open a Java file for translation"""
        file_path = filedialog.askopenfilename(
            title="Open Java File",
            filetypes=[("Java Files", "*.java"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    java_code = file.read()
                    self.java_text.delete("1.0", tk.END)
                    self.java_text.insert("1.0", java_code)
                    self.status_var.set(f"Opened: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Error opening file: {str(e)}")
                self.status_var.set("Error opening file")
    
    def save_file(self):
        """Save the generated Go code to a file"""
        go_code = self.go_text.get("1.0", tk.END).strip()
        if not go_code:
            messagebox.showwarning("Warning", "No Go code to save!")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save Go File",
            defaultextension=".go",
            filetypes=[("Go Files", "*.go"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    file.write(go_code)
                self.status_var.set(f"Saved: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving file: {str(e)}")
                self.status_var.set("Error saving file")
    
    def clear_text(self):
        """Clear both input and output text areas"""
        self.java_text.delete("1.0", tk.END)
        self.go_text.delete("1.0", tk.END)
        self.status_var.set("Ready")
    
    def show_about(self):
        """Show information about the application"""
        messagebox.showinfo(
            "About",
            "Java to Go Translator\n\n"
            "This application helps to translate Java code to Go.\n"
            "It is intended as a starting point for migration projects and\n"
            "may require additional manual adjustments to the code."
        )
    
    def show_help(self):
        """Show help information"""
        messagebox.showinfo(
            "How to Use",
            "1. Enter Java code in the top text area or load a template.\n"
            "2. Click 'Translate to Go' to generate Go code.\n"
            "3. The generated Go code will appear in the bottom text area.\n"
            "4. You can save the code to a file or copy it to clipboard.\n\n"
            "Note: The translator handles basic Java constructs but may not\n"
            "accurately translate all complex Java idioms. Always review\n"
            "and test the generated Go code."
        )
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

# Entry point
if __name__ == "__main__":
    app = JavaToGoTranslator()
    app.run()