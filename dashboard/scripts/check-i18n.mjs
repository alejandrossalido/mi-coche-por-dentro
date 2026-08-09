import fs from 'node:fs';
import path from 'node:path';
import ts from 'typescript';

const dashboardRoot = process.cwd();
const sourceRoot = path.join(dashboardRoot, 'src');
const i18nPath = path.join(sourceRoot, 'lib', 'i18n.tsx');

const parse = (file) => ts.createSourceFile(
  file,
  fs.readFileSync(file, 'utf8'),
  ts.ScriptTarget.Latest,
  true,
  file.endsWith('.tsx') ? ts.ScriptKind.TSX : ts.ScriptKind.TS
);

const i18nSource = parse(i18nPath);
const translationKeys = new Set();
const collectCatalog = (node) => {
  if (ts.isVariableDeclaration(node) && node.name.getText(i18nSource) === 'UI_TRANSLATIONS' && node.initializer) {
    const expression = ts.isAsExpression(node.initializer) ? node.initializer.expression : node.initializer;
    if (ts.isObjectLiteralExpression(expression)) {
      for (const property of expression.properties) {
        if (!ts.isPropertyAssignment(property)) continue;
        if (ts.isStringLiteral(property.name) || ts.isIdentifier(property.name)) translationKeys.add(property.name.text);
      }
    }
  }
  ts.forEachChild(node, collectCatalog);
};
collectCatalog(i18nSource);

const files = [];
const walk = (directory) => {
  for (const name of fs.readdirSync(directory)) {
    const file = path.join(directory, name);
    const stat = fs.statSync(file);
    if (stat.isDirectory()) walk(file);
    else if (/\.tsx?$/.test(name) && file !== i18nPath && !file.endsWith('telemetryLabels.ts')) files.push(file);
  }
};
walk(sourceRoot);

const spanishSignal = /[áéíóúñü¿¡]|\b(?:de|del|la|el|los|las|para|sin|con|datos|sesión|vehículo|prueba|motor|señal|estado|diagnóstico|captura|revisar|esperando|pendiente|selecciona|objetivo|batería|termostato|consumo|emisiones|ralentí|avería|lecturas|seguridad|calidad|cargando|guardar|añadir|cerrar|buscar|inicio|modo)\b/i;
const technical = /^(?:[a-z0-9_./:@#?&=\- ]+|[A-Z0-9_]+|\d+(?:\.\d+)?|[.#].*|.*(?:class|api|rgba|gradient).*)$/i;
const missing = [];
const seen = new Set();

for (const file of files) {
  const source = parse(file);
  const inspect = (node) => {
    let value = null;
    if (ts.isJsxText(node)) value = node.getText(source).replace(/\s+/g, ' ').trim();
    else if (ts.isStringLiteral(node) || ts.isNoSubstitutionTemplateLiteral(node)) value = node.text;
    if (value && value.length > 1 && spanishSignal.test(value) && !technical.test(value)
      && !translationKeys.has(value) && !seen.has(value)) {
      seen.add(value);
      const line = source.getLineAndCharacterOfPosition(node.getStart(source)).line + 1;
      missing.push(`${path.relative(dashboardRoot, file)}:${line} — ${value}`);
    }
    ts.forEachChild(node, inspect);
  };
  inspect(source);
}

const profilesPath = path.resolve(dashboardRoot, '..', 'collector', 'capture_profiles.py');
if (fs.existsSync(profilesPath)) {
  const profiles = fs.readFileSync(profilesPath, 'utf8');
  const profileText = /^\s*"(?:name|description|title|instruction)":\s*"([^"]+)"/gm;
  for (const match of profiles.matchAll(profileText)) {
    if (!translationKeys.has(match[1]) && !seen.has(match[1])) {
      seen.add(match[1]);
      missing.push(`collector/capture_profiles.py — ${match[1]}`);
    }
  }
}

if (missing.length) {
  console.error(`Missing translations (${missing.length}):\n${missing.join('\n')}`);
  process.exit(1);
}

console.log(`i18n coverage OK: ${translationKeys.size} catalog entries, ES/EN/IT/DE.`);
