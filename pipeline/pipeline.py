from parser.parser import Parser
from tokenizer.scanner import Lexer
from generator.generator import CodeGenerator

class Pipeline:
    def __init__(self, source_file):
        self.source_file = source_file
        self.tokens = None
        self.ast = None
        self.generated_code = None
        
    def run(self):
        stage = None
        try:
            print("Starting Lexical Analysis...")
            stage = "Lexical Analysis"
            lexer = Lexer()
            self.tokens = lexer.scan(self.source_file)
            print("Tokens Generated:")
            for token in self.tokens:
                print(f"  {token}")

            print("\nStarting Parsing...")
            stage = "Parsing"
            parser = Parser(self.tokens)
            self.ast = parser.parse()
            print("AST Generated:")
            parser.print_ast(self.ast)

            print("\nStarting Code Generation...")
            generator = CodeGenerator()
            generator.generate(self.ast)
            self.instructions = generator.get_code()
            print("Generated Code:")
            print(self.instructions)

            # TODO: optimize code and execute

            print("\nPipeline Execution Complete!")

        except Exception as e:
            print(f"Error during compilation pipeline at stage {stage}: {e}")