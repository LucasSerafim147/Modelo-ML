let dadosCasos = [];

async function carregarDados() {
    try {
        const res = await fetch("http://localhost:5000/api/casos");
        dadosCasos = await res.json();
        console.log("Dados carregados:", dadosCasos);
        atualizarGraficos();
    } catch (error) {
        console.error("Erro ao carregar dados:", error);
        alert("Não foi possível carregar os dados.");
    }
}

function filtrarPorData(casos) {
    const inicio = document.getElementById('dataInicio').value;
    const fim = document.getElementById('dataFim').value;

    return casos.filter(caso => {
        if (!caso.data_do_caso) return false;
        const data = new Date(caso.data_do_caso);
        const dataInicio = inicio ? new Date(inicio) : null;
        const dataFim = fim ? new Date(fim) : null;
        return (!dataInicio || data >= dataInicio) && (!dataFim || data <= dataFim);
    });
}
function atualizarGraficos() {
    const dadosFiltrados = filtrarPorData(dadosCasos);
    console.log("Dados filtrados:", dadosFiltrados);
   
}


document.getElementById("dataInicio").addEventListener("change", atualizarGraficos);
document.getElementById("dataFim").addEventListener("change", atualizarGraficos);


document.addEventListener('DOMContentLoaded', carregarDados);