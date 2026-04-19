const http = require("http");
const fs = require("fs");
const path = require("path");
const { randomUUID } = require("crypto");

const HOST = process.env.HOST || "0.0.0.0";
const PORT = Number(process.env.PORT || process.argv[2] || 8003);
const accounts = [];

function json(response, statusCode, payload) {
  const body = JSON.stringify(payload);
  response.writeHead(statusCode, {
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": Buffer.byteLength(body),
  });
  response.end(body);
}

function sendFile(response, filePath, contentType) {
  fs.readFile(filePath, (error, content) => {
    if (error) {
      json(response, 404, { detail: "Ressource introuvable." });
      return;
    }

    response.writeHead(200, { "Content-Type": contentType });
    response.end(content);
  });
}

function readJsonBody(request) {
  return new Promise((resolve, reject) => {
    let raw = "";

    request.on("data", (chunk) => {
      raw += chunk;
    });

    request.on("end", () => {
      if (!raw) {
        resolve({});
        return;
      }

      try {
        resolve(JSON.parse(raw));
      } catch (error) {
        reject(error);
      }
    });

    request.on("error", reject);
  });
}

function round(value) {
  return Math.round(Number(value) * 100) / 100;
}

function generateAccountNumber() {
  const datePart = new Date().toISOString().slice(0, 10).replace(/-/g, "");
  const randomPart = randomUUID().replace(/-/g, "").slice(0, 8).toUpperCase();
  return `ACC-${datePart}-${randomPart}`;
}

function accountSummary(account) {
  return {
    id: account.id,
    account_number: account.account_number,
    full_name: account.full_name,
    phone_number: account.phone_number,
    email: account.email,
    balance: account.balance,
    created_at: account.created_at,
  };
}

function accountDetails(account) {
  return {
    ...accountSummary(account),
    transactions: account.transactions,
  };
}

function findAccount(accountId) {
  return accounts.find((account) => account.id === accountId);
}

function docsHtml() {
  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <link rel="stylesheet" href="/public/swagger-ui/swagger-ui.css">
  <link rel="shortcut icon" href="/public/swagger-ui/favicon.svg">
  <title>API JavaScript - Swagger UI</title>
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="/public/swagger-ui/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({
      url: '/openapi.json',
      dom_id: '#swagger-ui',
      deepLinking: true,
      docExpansion: 'list',
      displayRequestDuration: true,
      filter: true,
      presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset]
    });
  </script>
</body>
</html>`;
}

const server = http.createServer(async (request, response) => {
  const url = new URL(request.url, `http://${HOST}:${PORT}`);
  const pathname = url.pathname;

  if (request.method === "GET" && pathname === "/") {
    json(response, 200, {
      message: "Bienvenue sur l'API bancaire JavaScript",
      documentation: "/docs",
      cahier_de_charges: "/cahier-de-charges",
    });
    return;
  }

  if (request.method === "GET" && pathname === "/docs") {
    const html = docsHtml();
    response.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
    response.end(html);
    return;
  }

  if (request.method === "GET" && pathname === "/openapi.json") {
    sendFile(response, path.join(__dirname, "openapi.json"), "application/json; charset=utf-8");
    return;
  }

  if (request.method === "GET" && (pathname === "/cahier-de-charges" || pathname === "/cahier-de-charges.pdf")) {
    sendFile(response, path.join(__dirname, "CAHIER_DE_CHARGES.pdf"), "application/pdf");
    return;
  }

  if (request.method === "GET" && pathname === "/cahier-de-charges.md") {
    sendFile(response, path.join(__dirname, "CAHIER_DE_CHARGES.md"), "text/markdown; charset=utf-8");
    return;
  }

  if (request.method === "GET" && pathname.startsWith("/public/")) {
    const relativePath = pathname.replace(/^\/+/, "");
    const filePath = path.join(__dirname, relativePath);
    const ext = path.extname(filePath);
    const contentTypeMap = {
      ".js": "text/javascript; charset=utf-8",
      ".css": "text/css; charset=utf-8",
      ".svg": "image/svg+xml",
    };
    sendFile(response, filePath, contentTypeMap[ext] || "application/octet-stream");
    return;
  }

  if (pathname === "/accounts" && request.method === "GET") {
    json(response, 200, accounts.map(accountSummary));
    return;
  }

  if (pathname === "/accounts" && request.method === "POST") {
    try {
      const payload = await readJsonBody(request);

      if (!payload.full_name || !payload.phone_number) {
        json(response, 400, { detail: "full_name et phone_number sont obligatoires." });
        return;
      }

      const initialBalance = round(payload.initial_balance || 0);
      if (initialBalance < 0) {
        json(response, 400, { detail: "Le solde initial doit etre positif ou nul." });
        return;
      }

      const account = {
        id: randomUUID(),
        account_number: generateAccountNumber(),
        full_name: payload.full_name,
        phone_number: payload.phone_number,
        email: payload.email || null,
        balance: initialBalance,
        created_at: new Date().toISOString(),
        transactions: [],
      };

      if (initialBalance > 0) {
        account.transactions.push({
          transaction_id: randomUUID(),
          transaction_type: "deposit",
          amount: initialBalance,
          description: "Solde initial",
          balance_after: initialBalance,
          created_at: new Date().toISOString(),
        });
      }

      accounts.push(account);
      json(response, 201, accountSummary(account));
    } catch {
      json(response, 400, { detail: "Corps JSON invalide." });
    }
    return;
  }

  const accountMatch = pathname.match(/^\/accounts\/([^/]+)$/);
  if (accountMatch && request.method === "GET") {
    const account = findAccount(accountMatch[1]);
    if (!account) {
      json(response, 404, { detail: "Compte introuvable." });
      return;
    }
    json(response, 200, accountDetails(account));
    return;
  }

  const txMatch = pathname.match(/^\/accounts\/([^/]+)\/(deposit|withdraw|transactions)$/);
  if (txMatch) {
    const account = findAccount(txMatch[1]);
    if (!account) {
      json(response, 404, { detail: "Compte introuvable." });
      return;
    }

    const action = txMatch[2];

    if (action === "transactions" && request.method === "GET") {
      json(response, 200, account.transactions);
      return;
    }

    if ((action === "deposit" || action === "withdraw") && request.method === "POST") {
      try {
        const payload = await readJsonBody(request);
        const amount = round(payload.amount);

        if (!Number.isFinite(amount) || amount <= 0) {
          json(response, 400, { detail: "Le montant doit etre strictement positif." });
          return;
        }

        if (action === "withdraw" && amount > account.balance) {
          json(response, 400, { detail: "Solde insuffisant pour effectuer ce retrait." });
          return;
        }

        account.balance = action === "deposit"
          ? round(account.balance + amount)
          : round(account.balance - amount);

        account.transactions.push({
          transaction_id: randomUUID(),
          transaction_type: action,
          amount,
          description: payload.description || null,
          balance_after: account.balance,
          created_at: new Date().toISOString(),
        });

        json(response, 200, accountDetails(account));
      } catch {
        json(response, 400, { detail: "Corps JSON invalide." });
      }
      return;
    }
  }

  json(response, 404, { detail: "Route introuvable." });
});

server.listen(PORT, HOST, () => {
  console.log(`API JavaScript disponible sur http://${HOST}:${PORT}`);
  console.log(`Swagger local : http://${HOST}:${PORT}/docs`);
});
