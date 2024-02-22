from mlx_lm import load, generate


def main():
    model, tokenizer = load("google/gemma-2b-it")
    text = generate(model, tokenizer, prompt="Why is the sky blue?")
    print(text)


if __name__ == "__main__":
    main()
