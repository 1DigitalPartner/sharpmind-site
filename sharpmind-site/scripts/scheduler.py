import subprocess, datetime

def run():
    print("⏳ Generating new SharpMind article…")
    subprocess.run(["python", "scripts/generate_post.py"])
    subprocess.run(["npm", "run", "build"])
    subprocess.run(["wrangler", "pages", "deploy", "build", "--project-name", "sharpmind", "--commit-dirty=true"])
    print("✔ Completed:", datetime.datetime.now())

if __name__ == "__main__":
    run()
