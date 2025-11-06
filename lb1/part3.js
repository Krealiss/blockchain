const API_KEY = process.env.ETHERSCAN_API_KEY;
const BASE = 'https://api.etherscan.io/v2/api'; // V2 mainnet
const CHAINID = '1'; // Ethereum mainnet
const KYIV_TZ = 'Europe/Kyiv';

// Limit rate of requests
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function toDec(hexStr) {
    return parseInt(hexStr, 16);
}

function fmtTimeFromHexTs(hexTs) {
    const tsMs = parseInt(hexTs, 16) * 1000;
    const d = new Date(tsMs);
    return new Intl.DateTimeFormat('uk-UA', {
        timeZone: KYIV_TZ,
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit', second: '2-digit'
    }).format(d);
}

async function etherscanGet(params) {
    const url = `${BASE}?${new URLSearchParams(params)}`;
    const res = await fetch(url, { method: 'GET' });
    if (!res.ok) throw new Error(`HTTP ${res.status} ${res.statusText}`);
    const json = await res.json();

    // V2: proxy methods return { result, error? }
    if (json && json.error) {
        const msg = json.error.message || JSON.stringify(json.error);
        throw new Error(`Etherscan proxy error: ${msg}`);
    }

    // Some responses may still contain status/message (for compatibility)
    if (json && json.status === '0') {
        const extra = json.result ? ` (${json.result})` : '';
        throw new Error(`Etherscan API error: ${json.message || 'NOTOK'}${extra}`);
    }

    if (json.result === undefined) {
        throw new Error(`Unexpected response: ${JSON.stringify(json).slice(0, 200)}...`);
    }
    return json.result;
}

async function getLatestBlockNumber() {
    const result = await etherscanGet({
        chainid: CHAINID,
        module: 'proxy',
        action: 'eth_blockNumber',
        apikey: API_KEY,
    });
    return toDec(result);
}

function toHexTag(num) {
    return '0x' + num.toString(16);
}

async function getBlockByNumberHex(tagHex, includeTxObjects = true) {
    const result = await etherscanGet({
        chainid: CHAINID,
        module: 'proxy',
        action: 'eth_getBlockByNumber',
        tag: tagHex,
        boolean: includeTxObjects ? 'true' : 'false',
        apikey: API_KEY,
    });
    return result; // block object (hex fields)
}

async function main() {
    try {
        if (!API_KEY) {
            console.error('API KEY problem');
            process.exit(1);
        }
        console.log('ETHERSCAN_API_KEY OK:', API_KEY.slice(0, 6) + '...');

        console.log(' I am receiving the number of the last block...');
        const latestNum = await getLatestBlockNumber();
        console.log(`Last block: ${latestNum}`);

        const latestBlock = await getBlockByNumberHex(toHexTag(latestNum), true);

        const blockNumberDec = toDec(latestBlock.number);
        const txCount = Array.isArray(latestBlock.transactions) ? latestBlock.transactions.length : 0;
        const timestampLocal = fmtTimeFromHexTs(latestBlock.timestamp);
        const hash = latestBlock.hash;
        const prevHash = latestBlock.parentHash;

        console.log('\n=== Information about the last block ===');
        console.log('Number (decimal):', blockNumberDec);
        console.log('Creation time (Europe/Kyiv):', timestampLocal);
        console.log('Number of transactions:', txCount);
        console.log('Block hash:', hash);
        console.log('Previous hash:', prevHash);

        // Average number of transactions for the last 5 blocks
        const howMany = 5;
        let totalTx = 0;

        console.log(`\nCounting the average number of transactions for the last ${howMany} blocks...`);
        for (let i = 0; i < howMany; i++) {
            const n = latestNum - i;
            const b = await getBlockByNumberHex(toHexTag(n), true);
            const cnt = Array.isArray(b.transactions) ? b.transactions.length : 0;
            totalTx += cnt;
            console.log(`Block ${toDec(b.number)}: txs=${cnt}`);
            await sleep(250); // Limit rate
        }
        const avg = totalTx / howMany;
        console.log(`Average number of transactions per ${howMany} blocks: ${avg.toFixed(2)}`);

        console.log('\n Complete.');
    } catch (err) {
        const msg = String(err && err.message ? err.message : err);

        if (/Invalid API Key|apikey/i.test(msg)) {
            console.error('Invalid or missing API key. Check ETHERSCAN_API_KEY.');
        }
        else {
            console.error('Eror:', msg);
        }
        process.exit(1);
    }
}

main();
