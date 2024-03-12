peso = float(input("Seu Peso: "))
altura = float(input("Sua Altura: "))

IMC = peso/(altura*altura)

print("IMC: ", IMC)

if IMC<18.5:
    print("Voce abaixo do peso")
elif 18.5<=IMC<=24.8:
    print("Voce esta no peso ideal")
else:
    print("Voce esta acima do peso")