2. How to select your own document to sign it and testML-DSA operates directly on raw message bytes, so you can sign any file type—including PDF documents (.pdf), Word files (.docx), images (.png/.jpg), text files (.txt), or ZIP archives.   Here is how you modify the code in Python or Terminal to use your own file:A. In Python / Jupyter NotebookReplace file.bin with the name or file path of your custom document:Pythonimport os
import subprocess

# 1. Specify your custom document path
my_document = "my_presentation.docx"  # Replace with "assignment.pdf", "photo.png", etc.

# 2. Sign your custom document with ML-DSA-65
cmd_sign = f'openssl pkeyutl -sign -in "{my_document}" -inkey key65.pem -out my_signature.sig'
res_code, out, err = run_cmd(cmd_sign)

if res_code == 0:
    print(
        f"[✓] Successfully created ML-DSA signature for '{my_document}'!"
    )
    print(
        f"    Signature file saved as 'my_signature.sig' ({os.path.getsize('my_signature.sig')} bytes)"
    )

# 3. Verify the signature against your custom document
cmd_verify = f'openssl pkeyutl -verify -in "{my_document}" -sigfile my_signature.sig -pubin -inkey pub65.pem'
res_verify, out_v, err_v = run_cmd(cmd_verify)

if res_verify == 0:
    print(
        f"[✓] Signature Verification PASSED: '{my_document}' is authentic and untampered."
    )
else:
    print(f"[X] Verification FAILED: {err_v}")
B. Directly in VS Code Terminal (Bash / WSL)If you prefer using the command line inside VS Code's integrated terminal (Ctrl + ~):   Bash# 1. Sign your PDF or Word document
openssl pkeyutl -sign -in "my_presentation.docx" -inkey key65.pem -out my_signature.sig

# 2. Verify the signature using the public key
openssl pkeyutl -verify -in "my_presentation.docx" -sigfile my_signature.sig -pubin -inkey pub65.pem
How to test tampering on your real document:Sign your original document document.docx to generate my_signature.sig.Open document.docx, add or delete a single character, and save it.Run the verification command again.Result: OpenSSL will return Signature Verification Failure because altering even a single byte changes the message hash $\mu$ computed during verification.   