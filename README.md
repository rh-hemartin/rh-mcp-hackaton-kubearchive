# MCP Example Server

## Install KubeArchive

```bash
git clone https://github.com/kubearchive/kubearchive --depth=1
kind create cluster
export KO_DOCKER_REPO="kind.local"
cd kubearchive
bash hack/quick-install.sh
bash test/log-generators/cronjobs/install.sh --num-jobs=3
cd ..
```

## Create an admin account

```bash
kubectl create serviceaccount admin-user -n kube-system
kubectl create clusterrolebinding admin-user --clusterrole=cluster-admin --serviceaccount=kube-system:admin-user
export KUBEARCHIVE_TOKEN=$(kubectl create -n kube-system token admin-user)
```

## Prepare Python

```bash
python -m venv venv
source venv/bin/activate
venv/bin/python -m pip install -r requirements.txt
```

## Configure Cursor or Run the MCP server

```bash
cat << EOF > .cursor/mcp.json
{
  "mcpServers": {
    "KubeArchive": {
      "command": "${PWD}/venv/bin/fastmcp",
      "args": ["run", "${PWD}/server.py"],
      "env": {
        "KUBEARCHIVE_URL": "https://localhost:8081",
        "KUBEARCHIVE_TOKEN": "${KUBEARCHIVE_TOKEN}"
      }
    }
  }
}
EOF
```

Note: you may need to reload cursor

## Port-forward KubeArchive

```bash
kubectl port-forward -n kubearchive svc/kubearchive-api-server 8081:8081 &
curl --insecure -H "Authorization: Bearer ${KUBEARCHIVE_TOKEN}" https://localhost:8081/apis/batch/v1/jobs | jq '.items | length'
```

## Notes

The MCP server is capable of getting a token from the call itself, which should be handed to the
LLM before calling the MCP server. The MCP server also checks if the KUBEARCHIVE_TOKEN environment
variable is defined, then it does not need a token in the parameters.
