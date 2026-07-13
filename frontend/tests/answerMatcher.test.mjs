import assert from "node:assert/strict";
import test from "node:test";

import { isAnswerAccepted } from "../utils/answerMatcher.js";


test("accepts exact and case-insensitive answers", () => {
  assert.equal(isAnswerAccepted("Python", "python"), true);
});

test("accepts one of multiple answer candidates", () => {
  assert.equal(isAnswerAccepted("merge sort", "QuickSort/Merge Sort/Heap Sort"), true);
});

test("rejects an unrelated short answer", () => {
  assert.equal(isAnswerAccepted("api", "dom"), false);
});
