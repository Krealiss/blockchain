import Web3 from "web3";

const web3 = new Web3("http://127.0.0.1:8545");

const abi = [
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "_newGreet",
                "type": "string"
            }
        ],
        "name": "setGreet",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "greet",
        "outputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
];

const contractAddress = "0x21820B81C054803d6Cf1b88a4d84141D405985c8"; 

const contract = new web3.eth.Contract(abi, contractAddress);

async function main() {
    try {
        const accounts = await web3.eth.getAccounts();
        const sender = accounts[0];
        console.log("Connected account:", sender);
        console.log("Contract address:", contractAddress);

        // перевіряємо, що код є
        const code = await web3.eth.getCode(contractAddress);
        console.log("Code at address:", code.slice(0, 20) + "...");
        if (code === "0x") {
            console.error("❌ No contract code at this address! Wrong address or Ganache was restarted.");
            return;
        }

        const greetData = contract.methods.greet().encodeABI();
        console.log("greet() call data:", greetData);

        console.log("Calling greet()...");
        const currentGreet = await contract.methods.greet().call();
        console.log("Initial greet():", currentGreet);

        console.log("Calling setGreet('Hello from Web3.js')...");
        const tx = await contract.methods
            .setGreet("Hello from Web3.js")
            .send({ from: sender });

        console.log("setGreet tx hash:", tx.transactionHash);

        const newGreet = await contract.methods.greet().call();
        console.log("New greet():", newGreet);
    } catch (err) {
        console.error("⚠ Error in script:", err);
    }
}

main();
