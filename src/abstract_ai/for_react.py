import os
import json
import PySimpleGUI as psg
import execjs  # For running JavaScript in Python

# JavaScript code to parse JS/TS/JSX/TSX files using @babel/parser
JS_CODE = """
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;
const types = require('@babel/types');

function parseCode(code) {
  const ast = parser.parse(code, {
    sourceType: 'module',
    plugins: ['jsx', 'typescript'],
  });

  const imports = [];
  const components = [];
  const dependencies = {};

  traverse(ast, {
    // Extract import declarations
    ImportDeclaration(path) {
      const source = path.node.source.value;
      path.node.specifiers.forEach(spec => {
        imports.push({
          name: spec.local.name,
          source: source,
          type: spec.type // e.g., ImportSpecifier, ImportDefaultSpecifier
        });
      });
    },

    // Extract React functional components (functions returning JSX)
    FunctionDeclaration(path) {
      const name = path.node.id.name;
      const hasJSX = path.node.body.body.some(statement => {
        return types.isReturnStatement(statement) && 
               statement.argument && 
               types.isJSXElement(statement.argument);
      });
      if (hasJSX) {
        components.push({ name, type: 'functional' });
        dependencies[name] = collectDependencies(path.node.body);
      }
    },

    // Extract React class components
    ClassDeclaration(path) {
      const name = path.node.id.name;
      const isComponent = path.node.superClass && (
        path.node.superClass.name === 'Component' ||
        path.node.superClass.name === 'PureComponent' ||
        (path.node.superClass.object && path.node.superClass.object.name === 'React' && 
         path.node.superClass.property.name === 'Component')
      );
      if (isComponent) {
        components.push({ name, type: 'class' });
        dependencies[name] = collectDependencies(path.node.body);
      }
    },
  });

  function collectDependencies(node) {
    const deps = new Set();
    traverse(node, {
      Identifier(path) {
        // Collect identifiers that might be dependencies (e.g., other components, hooks)
        if (!path.parentPath.isVariableDeclarator() && !path.parentPath.isFunctionDeclaration()) {
          deps.add(path.node.name);
        }
      },
      MemberExpression(path) {
        // Collect member expressions (e.g., React.useState)
        if (path.node.object.name === 'React' || path.node.object.name === 'use') {
          deps.add(`${path.node.object.name}.${path.node.property.name}`);
        }
      },
    }, { scope: null });
    return Array.from(deps);
  }

  return { imports, components, dependencies };
}
"""

# Compile the JavaScript code
ctx = execjs.compile(JS_CODE)

def parse_react_file(filepath):
    """Parse a JS/TS/JSX/TSX file and return imports, components, and dependencies."""
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()
    
    try:
        result = ctx.call('parseCode', code)
        return result['imports'], result['components'], result['dependencies']
    except Exception as e:
        print(f"Error parsing file {filepath}: {e}")
        return [], [], {}

def get_import_lines(filepath):
    """Extract import statements from the file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return [line.strip() for line in lines if line.strip().startswith(('import ', 'from '))]

def get_component_code(filepath, component_name):
    """Extract the code block for a specific component."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    code = ''
    recording = False
    indentation = ''
    brace_count = 0

    for line in lines:
        stripped = line.lstrip()
        # Start recording for function or class component
        if stripped.startswith(f'function {component_name}') or \
           stripped.startswith(f'const {component_name} =') or \
           stripped.startswith(f'class {component_name}'):
            recording = True
            indentation = line[:len(line) - len(stripped)]
            code += line
            if '{' in line:
                brace_count += line.count('{') - line.count('}')
        elif recording:
            code += line
            brace_count += (line.count('{') - line.count('}'))
            # Stop recording when the component block ends
            if brace_count == 0 and line.strip() == '':
                break
        # Stop if another function/class is encountered
        elif line.startswith(indentation + 'function ') or \
             line.startswith(indentation + 'const ') or \
             line.startswith(indentation + 'class '):
            if recording:
                break

    return code

class ReactAnalyser:
    def __init__(self, filepath):
        self.filepath = filepath
        self.imports, self.components, self.dependencies = parse_react_file(filepath)

    def get_components(self):
        return self.components

    def get_imports(self):
        return self.imports

    def get_component_deps(self, component_name):
        """Return dependencies for a specific component."""
        deps = self.dependencies.get(component_name, [])
        # Filter dependencies to include only known components or imports
        all_component_names = [c['name'] for c in self.components]
        all_import_names = [i['name'] for i in self.imports]
        return [dep for dep in deps if dep in all_component_names or dep in all_import_names]

# GUI Layout
layout = [
    [psg.FileBrowse(file_types=(("JavaScript/TypeScript Files", "*.js *.jsx *.ts *.tsx"),), key='-FILEBROWSE-')],
    [psg.Button("Load Components")],
    [psg.Listbox(values=[], size=(40, 10), key='-LIST-', enable_events=True, select_mode='multiple')],
    [psg.Multiline(size=(60, 20), key='-MULTI-', disabled=True)],
    [psg.Text('Save Location'), psg.InputText(os.getcwd(), key='-SAVEFOLDER-', disabled=True), psg.FolderBrowse('Browse', key='-FOLDERBROWSE-')],
    [psg.Text('Output Filename'), psg.InputText("output", key='-OUTPUTFILE-')],
    [psg.Button('Make Components'), psg.Button('Grab Dependencies'), psg.Button('Exit')],
]

window = psg.Window('React Component Browser', layout)

while True:
    event, values = window.read()
    
    if event in (psg.WINDOW_CLOSED, 'Exit'):
        break

    if event == 'Load Components':
        file = values['-FILEBROWSE-']
        if file.endswith(('.js', '.jsx', '.ts', '.tsx')):
            analyser = ReactAnalyser(file)
            window['-LIST-'].update([comp['name'] for comp in analyser.get_components()])
        else:
            psg.popup("Please select a JavaScript/TypeScript file.")

    if event == '-FOLDERBROWSE-':
        folder = values['-FOLDERBROWSE-']
        if folder:
            window['-SAVEFOLDER-'].update(folder)
            output_filename = values['-OUTPUTFILE-']
            if output_filename == 'output':
                i = 1
                while os.path.isfile(os.path.join(folder, f'{output_filename}_{i}.tsx')):
                    i += 1
                output_filename = f'{output_filename}_{i}'
            window['-OUTPUTFILE-'].update(output_filename)

    if event == '-LIST-':
        selected_components = values['-LIST-']
        analyser = ReactAnalyser(file)
        all_imports = set()
        all_deps = set()
        for comp in selected_components:
            deps = analyser.get_component_deps(comp)
            all_deps.update(deps)
            all_imports.update([i['name'] for i in analyser.get_imports() if i['name'] in deps])
        all_deps = list(all_imports) + list(all_deps)
        for comp in selected_components:
            if comp not in all_deps:
                all_deps.append(comp)
        window['-MULTI-'].update("\n".join(sorted(all_deps)))

    if event == 'Make Components':
        folder = values['-SAVEFOLDER-']
        output_filename = values['-OUTPUTFILE-']
        output_file = os.path.join(folder, f'{output_filename}.tsx')

        names = window['-MULTI-'].get().split("\n")
        import_lines = get_import_lines(file)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(line + '\n' for line in import_lines)
            f.write("\n")
            for name in names:
                comp_code = get_component_code(file, name)
                if comp_code:
                    f.write(comp_code)
                    f.write("\n\n")

        psg.popup(f"Components saved to {output_file}.")

window.close()
