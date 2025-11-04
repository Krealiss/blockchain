const crypto = require('crypto');

class Block {
    constructor(index, timestamp, data, previousHash = '') {
        this.index = index;
        this.timestamp = timestamp;
        this.data = data;                 // row or array of transactions
        this.previousHash = previousHash;
        this.nonce = 0;
        this.hash = this.calculateHash();
    }

    calculateHash() {
        const payload =
            String(this.index) +
            String(this.timestamp) +
            JSON.stringify(this.data) +
            String(this.previousHash) +
            String(this.nonce);

        return crypto.createHash('sha256').update(payload).digest('hex');
    }

    /**
     * Mine the block until the hash meets the condition.
     * @param {number} difficulty - complexity (for zero conditions)
     * @param {(hash:string)=>boolean} conditionFn - hash verification strategy
     * @returns {{iterations:number, ms:number}}
     */
    mineBlock(difficulty, conditionFn) {
        const start = Date.now();
        let iterations = 0;

        while (!conditionFn(this.hash)) {
            this.nonce++;
            iterations++;
            this.hash = this.calculateHash();
        }

        const ms = Date.now() - start;
        console.log(
            `Block mined: ${this.hash} | nonce=${this.nonce} | iterations=${iterations} | time=${ms}ms`
        );
        return { iterations, ms };
    }
}

class Blockchain {
    /**
     * @param {number} difficulty
     * @param {(hash:string, difficulty?:number)=>boolean} [conditionFn]
     */
    constructor(difficulty = 3, conditionFn) {
        this.difficulty = difficulty;
        this.conditionFn =
            conditionFn ||
            ((hash) => hash.startsWith('0'.repeat(this.difficulty)));

        this.chain = [this.createGenesisBlock()];
    }

    createGenesisBlock() {
        const genesis = new Block(
            0,
            new Date().toISOString(),
            'Genesis Block',
            '0'
        );
        // To ensure that the chain passes the complexity check, we also “mine” the genesis.
        genesis.mineBlock(this.difficulty, this.conditionFn);
        return genesis;
    }

    getLatestBlock() {
        return this.chain[this.chain.length - 1];
    }

    addBlock(data) {
        const newBlock = new Block(
            this.chain.length,
            new Date().toISOString(),
            data,
            this.getLatestBlock().hash
        );
        const stats = newBlock.mineBlock(this.difficulty, this.conditionFn);
        this.chain.push(newBlock);
        return stats; // iterations/time
    }

    isChainValid() {
        for (let i = 1; i < this.chain.length; i++) {
            const current = this.chain[i];
            const prev = this.chain[i - 1];

            // 1) previousHash correct
            if (current.previousHash !== prev.hash) {
                return false;
            }
            // 2) hash matches content
            if (current.hash !== current.calculateHash()) {
                return false;
            }
            // 3) hash corresponds to the selected “difficulty”/condition.
            if (!this.conditionFn(current.hash)) {
                return false;
            }
        }
        // verification of genesis
        const genesis = this.chain[0];
        if (!this.conditionFn(genesis.hash)) return false;
        if (genesis.hash !== genesis.calculateHash()) return false;

        return true;
    }
}

//Demonstration 
console.log('\nDemo #1: Difficulty-prefix (leading zeros)');
const difficulty = 3;
const chain1 = new Blockchain(difficulty);

let totalIters1 = 0;
let totalTime1 = 0;

const s1 = chain1.addBlock({ amount: 10, from: 'Alice', to: 'Bob' });
totalIters1 += s1.iterations; totalTime1 += s1.ms;

const s2 = chain1.addBlock(['tx1', 'tx2', 'tx3']); // transaction array
totalIters1 += s2.iterations; totalTime1 += s2.ms;

const s3 = chain1.addBlock('Just a string payload');
totalIters1 += s3.iterations; totalTime1 += s3.ms;

console.log('isChainValid() →', chain1.isChainValid()); // true

// Break the data of the second block
console.log('\n— Modifying data of block[1] to "Hacked!"');
chain1.chain[1].data = 'Hacked!';

console.log('isChainValid() after tampering →', chain1.isChainValid()); // false

console.log(
    `\n[Demo #1] Total iterations: ${totalIters1}, total mining time: ${totalTime1}ms`
);


const altCondition = (hash) => hash[2] === '3';

//Alternative miner
console.log('\n Demo #2: Alternative miner (3rd char is "3")');
const chain2 = new Blockchain(difficulty, altCondition);

let totalIters2 = 0;
let totalTime2 = 0;

const a1 = chain2.addBlock({ note: 'alt mining 1' });
totalIters2 += a1.iterations; totalTime2 += a1.ms;

const a2 = chain2.addBlock({ note: 'alt mining 2' });
totalIters2 += a2.iterations; totalTime2 += a2.ms;

const a3 = chain2.addBlock({ note: 'alt mining 3' });
totalIters2 += a3.iterations; totalTime2 += a3.ms;

console.log('isChainValid() (alt miner) →', chain2.isChainValid()); // true

console.log(
    `\n[Demo #2] Total iterations: ${totalIters2}, total mining time: ${totalTime2}ms`
);
