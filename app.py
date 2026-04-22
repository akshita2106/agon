const match = query.match(/(-?\d+\.?\d*)\s*([+\-*/])\s*(-?\d+\.?\d*)/);

if (!match) {
  return { output: "Invalid input." };
}

const a = parseFloat(match[1]);
const op = match[2];
const b = parseFloat(match[3]);

let result;

switch (op) {
  case '+': result = a + b; break;
  case '-': result = a - b; break;
  case '*': result = a * b; break;
  case '/': result = b !== 0 ? a / b : "undefined"; break;
}

return { output: `The sum is ${result}.` };
