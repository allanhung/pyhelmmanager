# pyhelmmanager
Generate helm template

### Install python module
```bash
pip install git+https://github.com/allanhung/pyhelmmanager.git
```

### Run with docker
```bash
docker build -t helm .
docker run -d --name=helm --rm -v $(pwd):/apps helm
docker exec -ti helm bash
```

## Usage
```bash
Generate helm chart by template
  create - create chart template
  patchrbacfile - patch kubernetes rbac file

Usage:
  pyhelmmanager chart create  (-p=<PROJECT>) [-k=<KIND>]
  pyhelmmanager chart patchrbacfile  (-p=<PROJECT>) (-f=<FILE>)

Options:
  -h, --help                              Show this screen.
  -k=<KIND>, --kind=<KIND>                Kubernetes objects type [default deploy]
  -p=<PROJECT>, --project=<PROJECT>       Project Name
  -f=<PROJECT>, --file=<FILE>             RBAC File to patch
```  

## Example
### kube-janitor
* create config file
```bash
cat > config_kube-janitor.yaml << EOF
chartVersion: 0.1.0
appVersion: 20.10.0
sources:
- https://codeberg.org/hjacobs/kube-janitor

values:
  image:
    repository: hjacobs/kube-janitor
  volumeMounts:
  - name: kube-janitor-config
    mountPath: /config
  
  volumes:
  - name: kube-janitor-config
    configMap:
      name: kube-janitor
  
  config:
    rules.yaml:
      rules:
      # delete all PVCs which are not mounted and not referenced by StatefulSets
      - id: remove-unused-pvcs
        resources:
        - persistentvolumeclaims
        jmespath: "_context.pvc_is_not_mounted && _context.pvc_is_not_referenced"
        ttl: 7d
EOF
```
* generate helm chart template
```bash
pyhelmmanager chart create -p kube-janitor -k deploy
```
* copy rbac yaml from repo
```bash
curl -o kube-janitor/templates/rbac.yaml https://codeberg.org/hjacobs/kube-janitor/raw/branch/main/deploy/rbac.yaml
```
* patch rbac file
```bash
pyhelmmanager chart patchrbacfile -p kube-janitor -f kube-janitor/templates/rbac.yaml
```
* check result
```bash
helm template --namespace=test kube-janitor -f kube-janitor/values.yaml kube-janitor
```
* Install
```bash
helm upgrade --install kube-janitor \
    --namespace test \
    --create-namespace \
    -f kube-janitor/values.yaml \
    kube-janitor/
```
