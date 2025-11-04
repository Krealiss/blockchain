const crypto = require('crypto');

// Validator
class Validator {
    constructor(name, stake) {
        if (stake <= 0) throw new Error('Stake must be > 0');
        this.name = name;
        this.stake = stake;
    }
}

/* Validator selection proportional to stake */
/** Returns the selected validator and totalStake (for reference) */
function selectValidator(validators) {
    const totalStake = validators.reduce((s, v) => s + v.stake, 0);
    const pickFloat =
        (crypto.randomInt(0, 1_000_000) / 1_000_000) * totalStake;

    let r = pickFloat;
    for (const v of validators) {
        r -= v.stake;
        if (r < 0) return { validator: v, totalStake };
    }
    // Фолбек (через можливі крайні випадки округлення)
    return { validator: validators.at(-1), totalStake };
}

// Block
class Block {
    constructor(index, timestamp, data, previousHash, validatorName) {
        this.index = index;
        this.timestamp = timestamp;
        this.data = data;
        this.previousHash = previousHash;
        this.validator = validatorName;
        this.hash = this.calculateHash();
    }

    calculateHash() {
        const payload =
            String(this.index) +
            String(this.timestamp) +
            JSON.stringify(this.data) +
            String(this.previousHash) +
            String(this.validator);
        return crypto.createHash('sha256').update(payload).digest('hex');
    }
}

/*Blockchain */
class Blockchain {
    constructor(validators) {
        if (!validators?.length) {
            throw new Error('Need at least one validator');
        }
        this.validators = validators;
        this.chain = [this.createGenesisBlock()];
    }

    createGenesisBlock() {
        const { validator } = selectValidator(this.validators);
        const block = new Block(
            0,
            new Date().toISOString(),
            'Genesis Block (PoS)',
            '0',
            validator.name
        );
        console.log(
            `Block ${block.index} validated by ${validator.name} (stake = ${validator.stake}). hash=${block.hash}`
        );
        return block;
    }

    getLatestBlock() {
        return this.chain[this.chain.length - 1];
    }

    addBlock(data) {
        const { validator } = selectValidator(this.validators);
        const block = new Block(
            this.chain.length,
            new Date().toISOString(),
            data,
            this.getLatestBlock().hash,
            validator.name
        );
        this.chain.push(block);
        console.log(
            `Block ${block.index} validated by ${validator.name} (stake = ${validator.stake}). hash=${block.hash}`
        );
        return block;
    }

    isChainValid() {
        // Checking the consistency and correctness of hashes
        for (let i = 1; i < this.chain.length; i++) {
            const curr = this.chain[i];
            const prev = this.chain[i - 1];

            // 1) previousHash is correct
            if (curr.previousHash !== prev.hash) return false;

            // 2) hash matches the recalculation
            if (curr.hash !== curr.calculateHash()) return false;
        }

        // Genesis block verification
        const g = this.chain[0];
        if (g.hash !== g.calculateHash()) return false;
        return true;
    }
}

// Demonstration

// Create a list of validators (Alice:5, Bob:10, Charlie:1)
const validators = [
    new Validator('Alice', 5),
    new Validator('Bob', 10),
    new Validator('Charlie', 1),
];

const posChain = new Blockchain(validators);

// Add at least 5 blocks
posChain.addBlock({ amount: 10, from: 'A', to: 'B' });
posChain.addBlock({ amount: 3, from: 'C', to: 'D' });
posChain.addBlock({ message: 'hello' });
posChain.addBlock(['tx1', 'tx2']);
posChain.addBlock('Just a payload');

// Checking validity → true
console.log('\nValidity after 5 blocks →', posChain.isChainValid());

// Breakdown of data for any block (for example, the 2nd = index 1)
console.log('\nTampering: change block[1].data = "Hacked!"');
posChain.chain[1].data = 'Hacked!';
console.log('Validity after tampering →', posChain.isChainValid()); // false


/* Proportionality check: win rates per 200 blocks */
const trials = 200;
const winCount = Object.fromEntries(validators.map(v => [v.name, 0]));

for (let i = 0; i < trials; i++) {
    const { validator } = selectValidator(validators);
    winCount[validator.name]++;
}

// Expected shares
const totalStake = validators.reduce((s, v) => s + v.stake, 0);
const expectedShare = Object.fromEntries(
    validators.map(v => [v.name, (v.stake / totalStake)])
);

console.log('\nWin frequency over', trials, 'blocks (no adding to chain, лише вибір)');
for (const v of validators) {
    const freq = winCount[v.name] / trials;
    const pct = (x) => (x * 100).toFixed(1) + '%';
    console.log(
        `${v.name} (stake=${v.stake}): wins=${winCount[v.name]}  ` +
        `freq=${pct(freq)}, expected≈${pct(expectedShare[v.name])}`
    );
}