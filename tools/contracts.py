import json
import os
from pathlib import Path
from typing import Any

from web3 import Web3
from web3.exceptions import ContractLogicError


def _load_abi(abi_path: str) -> list[dict[str, Any]]:
    path = Path(abi_path)
    if not path.is_absolute():
        path = Path.cwd() / path

    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and "abi" in payload and isinstance(payload["abi"], list):
        return payload["abi"]
    raise ValueError("Invalid ABI JSON format. Expected ABI list or object with 'abi' key.")


def _web3() -> Web3:
    rpc_url = os.getenv("RPC_URL", "").strip()
    if not rpc_url:
        raise ValueError("Missing RPC_URL in environment.")
    w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 20}))
    if not w3.is_connected():
        raise ConnectionError("Unable to connect to RPC endpoint.")
    return w3


def get_contract_state(address: str, abi_path: str) -> dict[str, Any]:
    try:
        w3 = _web3()
        abi = _load_abi(abi_path)
        checksum = Web3.to_checksum_address(address)
        contract = w3.eth.contract(address=checksum, abi=abi)

        state: dict[str, Any] = {
            "ok": True,
            "address": checksum,
            "eth_balance_wei": w3.eth.get_balance(checksum),
            "chain_id": w3.eth.chain_id,
            "read_calls": {},
        }

        # Try common zero-arg view functions to give quick diagnostics.
        common_fns = [
            "name",
            "symbol",
            "decimals",
            "totalSupply",
            "owner",
            "paused",
            "collateralRatio",
        ]
        for fn_name in common_fns:
            fn = getattr(contract.functions, fn_name, None)
            if fn is None:
                continue
            try:
                state["read_calls"][fn_name] = fn().call()
            except Exception:
                pass

        return state
    except Exception as exc:
        return {"ok": False, "error": f"Failed to read contract state: {exc}"}


def call_contract_function(address: str, abi_path: str, fn_name: str) -> dict[str, Any]:
    fn_name = fn_name.strip()
    if not fn_name:
        return {"ok": False, "error": "fn_name is required."}

    try:
        w3 = _web3()
        abi = _load_abi(abi_path)
        checksum = Web3.to_checksum_address(address)
        contract = w3.eth.contract(address=checksum, abi=abi)

        fn = getattr(contract.functions, fn_name, None)
        if fn is None:
            return {"ok": False, "error": f"Function '{fn_name}' not found in ABI."}

        value = fn().call()
        return {
            "ok": True,
            "address": checksum,
            "function": fn_name,
            "result": value,
        }
    except ContractLogicError as exc:
        return {"ok": False, "error": f"Contract call failed: {exc}"}
    except TypeError:
        return {
            "ok": False,
            "error": (
                f"Function '{fn_name}' likely requires arguments. "
                "Current tool supports zero-argument view/pure functions only."
            ),
        }
    except Exception as exc:
        return {"ok": False, "error": f"Failed to call contract function: {exc}"}
