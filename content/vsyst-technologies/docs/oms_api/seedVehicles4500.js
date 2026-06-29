// One-off seed: 4500 vehicles TE57UU0001 .. TE57UU4500 into the TESTING Atlas DB
// via the real createVehicle API (POST /api/v3/veh_msts), same as the test seed.
//
// Run:  NODE_ENV=testing node ./test/api_v3/temp/seed/seedVehicles4500.js
//
// This connects mongoose to the .env.testing DATABASE_URI (a shared Atlas
// cluster) and writes 4500 veh_msts + 4500 veh_trns. Review before running.

process.env.NODE_ENV = "testing";
require("dotenv").config({ path: ".env.testing" });

const mongoose = require("mongoose");
const supertest = require("supertest");

const CUST_ID = "6634d3049e2f14abb0ab03e0";
const PREFIX = "TE57UU";
const START = 1;
const END = 4500; // inclusive -> exactly 4500 vehicles
const CONCURRENCY = 20; // requests in flight per batch

const dheader = { "x-api-key": process.env["X_API_KEY_3"] };

const regNo = (i) => `${PREFIX}${String(i).padStart(4, "0")}`;

(async () => {
  const uri = process.env.DATABASE_URI;
  if (!uri) throw new Error("DATABASE_URI missing from .env.testing");
  console.log(`Connecting to: ${uri.replace(/\/\/([^:]+):[^@]+@/, "//$1:***@")}`);
  await mongoose.connect(uri);
  console.log("DB connected. Target DB:", mongoose.connection.name);

  const app = require("../../../dzzlo_oms_test");
  const request = supertest(app);

  let ok = 0;
  const failures = [];

  for (let start = START; start <= END; start += CONCURRENCY) {
    const batch = [];
    for (let i = start; i < start + CONCURRENCY && i <= END; i++) {
      const veh_reg_no = regNo(i);
      batch.push(
        request
          .post("/api/v3/veh_msts")
          .send({ cust_id: CUST_ID, veh_reg_no })
          .set(dheader)
          .then((res) => {
            if (res.status === 201) ok++;
            else failures.push({ veh_reg_no, status: res.status, body: res.body });
          })
          .catch((err) => failures.push({ veh_reg_no, error: err.message }))
      );
    }
    await Promise.all(batch);
    console.log(
      `Progress: ${Math.min(start + CONCURRENCY - 1, END)}/${END} | ok=${ok} fail=${failures.length}`
    );
  }

  console.log("\n==== DONE ====");
  console.log(`Created: ${ok}`);
  console.log(`Failed:  ${failures.length}`);
  if (failures.length) {
    console.log("Sample failures:", JSON.stringify(failures.slice(0, 10), null, 2));
  }

  await mongoose.disconnect();
  process.exit(failures.length ? 1 : 0);
})().catch(async (e) => {
  console.error("FATAL:", e);
  try { await mongoose.disconnect(); } catch {}
  process.exit(1);
});
