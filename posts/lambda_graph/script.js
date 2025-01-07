
let idCounter = 0;

function getUniqueId() {
    return idCounter++;
}

let env = {
    nodes: new vis.DataSet(),
    edges: new vis.DataSet()
};




function removeEdge(edges,from,to){
    edges.forEach(edge => {
        if(edges.from == from && edge.to == to){
            edges.remove(edge.id);
        }
    });
}


class GraphEntity{
    constructor(env){
        this.id = getUniqueId();
        this.env = env;
        this.refCounter=0;
        this.freeVar = new Set()
    }
    attach(node){
        if(!this.env.nodes.get(node.graphNode)){
            this.env.nodes.add(node.graphNode);
        }
        this.env.edges.add({from:this.id,to:node.id})
        node.refCounter++;
    }
    detach(node){
        var e = {from:this.id, to:node.id};
        removeEdge(this.env.edges,this.id,node.id);
        node.refCounter--;
        if(node.refCounter == 0){
            this.env.nodes.remove(node.id);
        }
    }
}


class Var extends GraphEntity{
    constructor(name, env) {
        super(env);
        this.name = name
        this.graphNode = { id: this.id, label: name };
        env.nodes.add(this.graphNode);
        this.freeVar.add(name)
    }
    toString(){
        return this.name;
    }
    copy(){
        return new Var(this.name,this.env);
    }
    copy_shallow(){
        return this.copy();
    }
    alpha_conv(p,pn){
        if(this.name == p){
            this.freeVar.delete(this.name);
            this.freeVar.add(pn);
            this.name = pn
            this.env.nodes.update({id:this.id, label:pn});
        }
    }
    subs(p,e){
        if(p == this.name){
            return e.copy();
        } else {
            return this;
        }
    }
}

class Lambda extends GraphEntity {
    constructor(param, body, env) {
        super(env);
        const label = `λ${param}`;
        this.param = param
        this.body = body
        const edges = [{ from: this.id, to: body.id }];
        this.graphNode = { id: this.id, label: label };
        env.nodes.add(this.graphNode);
        this.attach(body)
        this.freeVar = new Set(body.freeVar);
        this.freeVar.delete(param);
    }
    toString(){
        return "(Lambda " + this.param + " " + this.body.toString() + ")";
    }
    copy(){
        return new Lambda(this.param,this.body.copy(),this.env)
    }
    copy_shallow(){
        this.body.refCounter++;
        return new Lambda(this.param,this.body,this.env)
    }

    subs(p,e){
        tmp = this.body.subs(p,e);
        if(tmp != this.body){
            detach(this.body);
            attach(this.tmp);
        }
        return this;
    }
    
    alpha_conv(p,pn){
        if(p == this.param){
            this.param = pn;
            this.body.alpha_conv(p,pn);
            this.env.nodes.update({id:this.id,label:`λ${param}`});
        } else {
            if(this.freeVar.has(p)){
                this.body.alpha_conv(p,pn);
            }
        }
    }
}

class App extends GraphEntity  {
    constructor(func, arg, env) {
        super(env);
        this.func = func
        this.arg = arg
        const label = "@";
        this.graphNode = { id: this.id, label: label };
        env.nodes.add(this.graphNode);
        const edges = [
            { from: this.id, to: func.id },
            { from: this.id, to: arg.id }
        ];
        env.edges.add(edges);
        this.func.refCounter++;
        this.arg.refCounter++;
        this.compute_freevar();
    }
    toString(){
        return "(" + this.func.toString() + " " + this.arg.toString() + ")";
    }
    compute_freevar(){
        this.freeVar = this.func.freeVar.union(this.arg.freeVar);
    }
    copy(){
        return new App(this.func.copy(),this.arg.copy(),this.env)
    }
    copy_shallow(){
        this.func.refCounter++;
        this.arg.refCounter++;
        return new App(this.func,this.arg,this.env)
    }
    alpha_conv(p,pn){
        if(this.func.freeVar.has(p)){
            this.func.alpha_conv(p,pn);
        }
        if(this.arg.freeVar.has(p)){
            this.arg.alpha_conv(p,pn);
        }
        this.compute_freevar();
    }
    subs(p,e){
        if(this.func.freeVar.has(p)){
            var tmp = this.func.subs(p,e);
            if(tmp != this.func){
                this.detach(this.func);
                this.attach(tmp);
                this.func = tmp;
            }
        }
        if(this.arg.freeVar.has(p)){
            var tmp =  this.arg.subs(p,e);
            if(tmp != this.arg){
                this.detach(this.arg);
                this.attach(tmp);
                this.arg = tmp;
            }
        }
        this.compute_freevar();
        return this;
    }

    app(){
        if(this.func instanceof Lambda){
            this.func.body.subs(this.func.param,this.arg);
            this.detach(this.arg);
            return this.func.body;
        }
        return this;
    }
}


function app(ast){
    var tmp = ast.app();
    if(tmp == ast){
        return tmp;
    } else {
        ast.env.nodes.remove(ast.id);
        tmp.refCounter++;
        return tmp;
    }
}

function convertToAST(sexpr, env) {
    if (typeof sexpr === "string") {
        return new Var(sexpr, env);
    } else if (typeof sexpr[0] === "string" &&  sexpr[0] === "lambda") {
        const body = convertToAST(sexpr[2], env);
        return new Lambda(sexpr[1], body, env);
    } else if (Array.isArray(sexpr) && sexpr.length === 2) {
        const left = convertToAST(sexpr[0], env);
        const right = convertToAST(sexpr[1], env);
        return new App(left, right, env);
    } else {
        throw new Error("Expression S-expr invalide : " + JSON.stringify(sexpr));
    }
}


// Exemple d'utilisation de Vis.js pour afficher le graphique
container = document.getElementById('mynetwork');

const options = {
    "layout": {
        "hierarchical": {
            "direction": "LR",
            "sortMethod": "directed",
            "nodeSpacing": 200,
            "treeSpacing": 400
        }
    },
    "nodes": {
        "shape": 'circle',
        "size": 20
    },
    "edges": {
        "arrows": 'to'
    },
};



const network = new vis.Network(container, env, options);

// Redimensionner correctement après l'initialisation
function resizeNetwork() {
    network.setSize(container.offsetWidth, container.offsetHeight);
    network.redraw();
}

// Initialiser le redimensionnement à la taille du conteneur
resizeNetwork();

// Redimensionner en cas de changement de taille de la fenêtre
window.addEventListener('resize', resizeNetwork);







function parseSExpression(input) {
    let tokens = input.match(/\(|\)|[^\s()]+/g);
    if (!tokens) return null;

    function parse(tokens) {
        let token = tokens.shift();
        if (token === "(") {
            let expr = [];
            while (tokens[0] !== ")") {
                expr.push(parse(tokens));
            }
            tokens.shift(); // Enlever la parenthèse fermante
            return expr;
        } else {
            return token;
        }
    }
    return parse(tokens);
}

// Exemple de conversion d'une expression
const expr = [["lambda", "x", ["x", "x"]],["lambda","z" ,"y"]];
//a = convertToAST(expr, env);
var e = parseSExpression("(lambda x (lambda y (x (z x))))")
var a = convertToAST(e,env)

/*setTimeout(() => {
    a = app(a);
    console.log(a.toString());
    network.redraw();
}, 5000); // 2000 ms = 2 secondes
*/


network.redraw()

