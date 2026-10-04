import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("Simulador de concentración de mercado Grupo J")

def cr_k(S,k):
    ordenadas = np.sort(S, axis=1)[:,::-1]
    return ordenadas[:,:k].sum(axis=1)

def ihh(S):
    return(S**2).sum(axis=1)*10000

def dominancia(S):
    h = (S**2)/(S**2).sum(axis=1,keepdims=True)
    return(h**2).sum(axis=1)

def entropia(S):
    logs = np.log(S, where=S > 0,out=np.zeros_like(S))
    return-(S*logs).sum(axis=1)

indicadores=st.multiselect(
"Elige uno o mas indicadores:",
["Ratio de concentración (CRk)", "Índice de IHH",
"Índice de Dominancia", "Índice de Entropía"],
default=["Índice de IHH"],
)

N=st.number_input(
"Número de empresas (N):",
min_value=2, max_value=100, value=10, step=1,
)

k = st.number_input("k para el ratio CRk:",
      min_value=1, max_value=N, value=min(3,N),step=1)

iteraciones = st.number_input("Número de iteraciones:",
      min_value=100, max_value=100000,
      value=1000, step=100)

st.warning("Más iteraciones y más empresas hacen la simulación más lenta "
      "y consumen más memoria y procesador de tu computador.")

if not indicadores:
    st.warning("Elige al menos un indicador.")

if st.button("Ejecutar simulación"):
    st.session_state["S"]=np.random.dirichlet(np.ones(N), size=iteraciones)

if "S" in st.session_state and indicadores and caso is not None:
    S=st.session_state["S"]
    calculos={
      "Ratio de concentración (CRk)": lambda T:cr_k(T, k),
      "Índice de IHH":lambda T:ihh(T),
      "Índice de Dominancia":lambda T:dominancia(T), 
      "Índice de Entropía":lambda T:entropia(T),
}
    for nombre in indicadores:
        valores=calculos[nombre](S)
        valor_caso=calculos[nombre](caso.reshape(1,-1))[0]
        percentil=(valores<valor_caso).mean()*100

        fig,ax=plt.subplots()
        ax.hist(valores,bins=30)
        ax.set_title(nombre)
        ax.set_xlabel("Valor del indicador")
        ax.set_ylabel("Frecuencia")
        st.pyplot(fig)
        st.write(f"El caso particular vale {valor_caso:.3f} y está en el percentil {percentil:.1f}.")

st.subheader("Caso particular")
modo=st.radio("¿Cómo quieres definir este caso?",
       ["Ingresar cuotas a mano","Generar al azar"])

if modo=="Generar al azar":
    if (st.button("Generar nuevo caso")
            or "caso_azar" not in st.session_state
            or len(st.session_state["caso_azar"])!=N):
        st.session_state["caso_azar"]=np.random.dirichlet(np.ones(N))
    caso=st.session_state["caso_azar"]
    st.write("Cuotas generadas (%)",np.round(caso*100,2))

elif modo=="Ingresar cuotas a mano":
    texto=st.text_input(
      f"Escribe {N} coutas en % separadas por comas:",
      value=",".join([str(round(100/N,4))]*N)
)
    try:
       caso=np.array([float(x) for x in texto.split(",")])/100
    except ValueError:
       caso=None
       st.error("Escribe solo números separados por comas.")
    else:
      if len(caso) !=N:
         st.error(f"Debes escribir exactamente {N} cuotas.")
         caso=None
      elif abs(caso.sum()-1)>0.001:
       st.error(f"Las cuotas suman {caso.sum()*100:.2f}%, deben sumar 100%.")
       caso=None

st.subheader("Evaluador")
if caso is not None:
    ihh_caso = ihh(caso.reshape(1,-1))[0]
    respuesta=st.radio("¿Qué nivel de concentración tiene el caso particular?",
        ["Baja","Moderada","Alta"], index=None)
    correcta="Baja" if ihh_caso<1500 else "Moderada" if ihh_caso<=2500 else "Alta"
    if respuesta:
        if respuesta==correcta:
            st.success("¡Correctoo! :)")
        else:
            st.error(f"Incorrecto. La respuesta correcta es: {correcta}.")
        st.write(f"IHH={ihh_caso:.0f}. Menos de 1.500 es baja, de 1.500 a 2.500 moderada y más de 2.500 alta.")
