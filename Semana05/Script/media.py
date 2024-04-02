lista = [1,2,3,4,2.3,3,5,4,1,2,3,4, 100]

soma = 0
for numero in lista:
    soma += numero

print("Média: ", round(soma/len(lista),2))