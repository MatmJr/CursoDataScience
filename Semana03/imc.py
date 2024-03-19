peso = float(input("Digite o seu peso: "))
altura = float(input("Digite a sua altura: "))

imc = peso/(altura*altura)
print(round(imc,2))

if imc<19:
    print("Abaixo do peso")
if imc>=19 and imc<=25:
    print("Peso Normal")
else:
    print("Acima do peso")