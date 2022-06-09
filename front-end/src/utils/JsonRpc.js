const jsonrpc_url = "/api/v1/jsonrpc"

export async function call_method(method, params) {
    let data = {
        jsonrpc: "2.0",
        method: method,
        params: params,
        id: Math.floor(Math.random() * 101)
    };

    let response = await (await fetch(jsonrpc_url, {
        method: "POST",
        body: JSON.stringify(data),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    })).json();

    return response;
}