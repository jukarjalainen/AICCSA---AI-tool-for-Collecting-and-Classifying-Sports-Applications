import OpenAI from "openai";
const client = new OpenAI();
import { promt1, promt2,  description, appId } from "./promts.mjs";

try {
  const response = await client.responses.create({
    model: "gpt-5",
    reasoning: { effort: "high" },
    text: { format: { type: "json_object" } },
    input: promt2 + "\n App ID: " + appId + "\n Description: " + description,
  });
  console.log(response.output_text);
} catch (err) {
  console.error("OpenAI request failed:", err);
  process.exit(1);
}
