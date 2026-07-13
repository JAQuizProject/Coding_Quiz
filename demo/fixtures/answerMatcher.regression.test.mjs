import assert from "node:assert/strict";
import test from "node:test";

import { isAnswerAccepted } from "../../frontend/utils/answerMatcher.js";


const cases = [
  ["10", "10", true],
  ["10.00", "10", true],
  ["10.009", "10", true],
  ["10.02", "10", false],
  ["1,000", "1000", true],
  ["java3", "python3", false],
  ["status 404", "http 404", false],
];

for (const [userAnswer, expectedAnswer, accepted] of cases) {
  test(`${userAnswer} vs ${expectedAnswer} -> ${accepted}`, () => {
    assert.equal(isAnswerAccepted(userAnswer, expectedAnswer), accepted);
  });
}
