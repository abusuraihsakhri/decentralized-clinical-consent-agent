"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const html = fs.readFileSync("web/index.html", "utf8");
const matches = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
assert.equal(matches.length, 1, "Expected one inline script");

const initial = {
  task: "DEMO-001", target: "SAMPLE-001", primary: "29.4", secondary: "14.8",
  descriptor: "DISCORDANT_ANOMALY"
};
const nodes = new Map();
function node(id) {
  if (!nodes.has(id)) {
    nodes.set(id, {
      value: initial[id] || "",
      checked: id === "critical",
      disabled: id === "download",
      textContent: "",
      className: "",
      events: {},
      addEventListener(event, callback) { this.events[event] = callback; },
      click() {},
      remove() {}
    });
  }
  return nodes.get(id);
}
const document = {
  getElementById: node,
  createElement: () => ({click() {}, remove() {}}),
  body: {appendChild() {}}
};
vm.runInNewContext(matches[0][1], {
  document,
  Blob,
  URL: {createObjectURL: () => "blob:demo", revokeObjectURL() {}},
  setTimeout: callback => callback()
});

function evaluate() { node("audit-form").events.submit({preventDefault() {}}); return JSON.parse(node("output").textContent); }
let result = evaluate();
assert.equal(result.mode, "LOCAL_RULES_PREVIEW");
assert.equal(result.is_clinical_consent_verification, false);
assert.equal(result.total_alerts, 3);
assert.equal(result.critical_alerts_count, 1);
assert.equal(result.overall_urgency, "CRITICAL_STAT_PANIC");
assert.equal(node("runs").textContent, "1");
assert.equal(node("download").disabled, false);

node("primary").value = "1";
node("secondary").value = "1";
node("descriptor").value = "NOMINAL";
node("critical").checked = false;
result = evaluate();
assert.equal(result.total_alerts, 0);
assert.equal(result.overall_urgency, "ROUTINE");

node("primary").value = "";
node("audit-form").events.submit({preventDefault() {}});
assert.match(node("status").textContent, /required/);
assert.equal(node("runs").textContent, "2");

node("download").events.click();
console.log("Browser rules-preview smoke test passed");
