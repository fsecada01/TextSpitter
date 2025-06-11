<div id="top">

<!-- HEADER STYLE: MODERN -->
<div align="left" style="position: relative; width: 100%; height: 100%; ">

<img src="readmeai/assets/logos/purple.svg" width="30%" style="position: absolute; top: 0; right: 0;" alt="Project Logo"/>

# TEXTSPITTER.GIT

<em>Transforming documents into insights, effortlessly and efficiently.<em>

<!-- BADGES -->
<img src="https://img.shields.io/github/license/fsecada01/TextSpitter.git?style=flat-square&logo=opensourceinitiative&logoColor=white&color=8a2be2" alt="license">
<img src="https://img.shields.io/github/last-commit/fsecada01/TextSpitter.git?style=flat-square&logo=git&logoColor=white&color=8a2be2" alt="last-commit">
<img src="https://img.shields.io/github/languages/top/fsecada01/TextSpitter.git?style=flat-square&color=8a2be2" alt="repo-top-language">
<img src="https://img.shields.io/github/languages/count/fsecada01/TextSpitter.git?style=flat-square&color=8a2be2" alt="repo-language-count">

<em>Built with the tools and technologies:</em>

<img src="https://img.shields.io/badge/TOML-9C4121.svg?style=flat-square&logo=TOML&logoColor=white" alt="TOML">
<img src="https://img.shields.io/badge/Pytest-0A9EDC.svg?style=flat-square&logo=Pytest&logoColor=white" alt="Pytest">
<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat-square&logo=Python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/GitHub%20Actions-2088FF.svg?style=flat-square&logo=GitHub-Actions&logoColor=white" alt="GitHub%20Actions">
<img src="https://img.shields.io/badge/uv-DE5FE9.svg?style=flat-square&logo=uv&logoColor=white" alt="uv">

</div>
</div>
<br clear="right">

---

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
    - [Project Index](#project-index)
- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Usage](#usage)
    - [Testing](#testing)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Overview

TextSpitter is a powerful developer tool designed to simplify document processing and enhance file handling capabilities across various formats.

**Why TextSpitter?**

This project streamlines the way developers interact with documents, ensuring a robust and efficient development experience. The core features include:

- 📦 **Robust Dependency Management:** Ensures a stable development environment with essential libraries for seamless functionality.
- 📄 **File Extraction Capabilities:** Standardizes handling of text, CSV, DOCX, and PDF files for smooth integration.
- 🛠️ **Enhanced Logging:** Utilizes loguru for sophisticated error tracking, improving debugging and maintenance.
- 🚀 **Automated Publishing:** Streamlines the release process with GitHub Actions for continuous delivery.
- 🖥️ **Code Quality Tools:** Integrates black and ruff for consistent code formatting and linting.

---

## Features

|      | Component       | Details                              |
| :--- | :-------------- | :----------------------------------- |
| ⚙️  | **Architecture**  | <ul><li>Modular design for text processing</li><li>Utilizes a pipeline approach for data flow</li></ul> |
| 🔩 | **Code Quality**  | <ul><li>Adheres to PEP 8 style guidelines</li><li>Includes type hints for better readability</li></ul> |
| 📄 | **Documentation** | <ul><li>Basic README file present</li><li>Inline comments for complex functions</li></ul> |
| 🔌 | **Integrations**  | <ul><li>CI/CD with GitHub Actions</li><li>Package management via pip</li></ul> |
| 🧩 | **Modularity**    | <ul><li>Core functionalities separated into modules</li><li>Reusable components for text manipulation</li></ul> |
| 🧪 | **Testing**       | <ul><li>Unit tests using pytest</li><li>Mocking capabilities with pytest-mock</li></ul> |
| ⚡️  | **Performance**   | <ul><li>Efficient handling of large text files</li><li>Optimized algorithms for text parsing</li></ul> |
| 🛡️ | **Security**      | <ul><li>Input validation to prevent injection attacks</li><li>Dependencies regularly updated for security patches</li></ul> |
| 📦 | **Dependencies**  | <ul><li>Core libraries: <code>pymupdf</code>, <code>lxml</code>, <code>python-docx</code></li><li>Development tools: <code>pytest</code>, <code>loguru</code></li></ul> |
| 🚀 | **Scalability**   | <ul><li>Designed to handle increasing text data volumes</li><li>Supports multi-threading for concurrent processing</li></ul> |
```

---

## Project Structure

```sh
└── TextSpitter.git/
    ├── .github
    │   └── workflows
    ├── _config.yml
    ├── core_requirements.in
    ├── core_requirements.txt
    ├── dev_requirements.in
    ├── dev_requirements.txt
    ├── LICENSE
    ├── pyproject.toml
    ├── readme-ai.md
    ├── README.md
    ├── requirements.txt
    ├── setup_py.backup
    ├── TextSpitter
    │   ├── __init__.py
    │   ├── core.py
    │   ├── logger.py
    │   └── main.py
    └── uv.lock
```

### Project Index

<details open>
	<summary><b><code>TEXTSPITTER.GIT/</code></b></summary>
	<!-- __root__ Submodule -->
	<details>
		<summary><b>__root__</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ __root__</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/fsecada01/TextSpitter.git/blob/master/core_requirements.in'>core_requirements.in</a></b></td>
					<td style='padding: 8px;'>- Defines essential dependencies for the project, ensuring a robust environment for document processing and testing<br>- By incorporating libraries such as loguru for logging, PyMuPDF and pypdf for PDF manipulation, and python-docx for Word document handling, it streamlines development and enhances functionality<br>- Additionally, it includes testing frameworks like pytest to facilitate effective testing practices, contributing to overall code quality and reliability.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/fsecada01/TextSpitter.git/blob/master/core_requirements.txt'>core_requirements.txt</a></b></td>
					<td style='padding: 8px;'>- Defines essential dependencies for the project, ensuring that all necessary libraries are available for seamless functionality and testing<br>- By managing package versions, it facilitates a consistent development environment, supporting various components like logging, document processing, and testing frameworks<br>- This contributes to the overall stability and reliability of the codebase architecture, enabling efficient development and maintenance processes.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/fsecada01/TextSpitter.git/blob/master/dev_requirements.in'>dev_requirements.in</a></b></td>
					<td style='padding: 8px;'>- Defines development dependencies for the project, ensuring a consistent environment for contributors<br>- By referencing core requirements and including essential tools like black for code formatting and ruff for linting, it streamlines the setup process<br>- This facilitates collaboration and enhances code quality across the codebase, ultimately supporting efficient development practices within the overall architecture.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/fsecada01/TextSpitter.git/blob/master/dev_requirements.txt'>dev_requirements.txt</a></b></td>
					<td style='padding: 8px;'>- Facilitates the management of development dependencies for the project by specifying required packages and their versions<br>- This ensures a consistent environment for developers, enhancing collaboration and reducing setup issues<br>- By automating the generation of this requirements file, it streamlines the process of maintaining and updating dependencies, ultimately supporting the overall architecture of the codebase focused on Jupyter-related functionalities.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/fsecada01/TextSpitter.git/blob/master/LICENSE'>LICENSE</a></b></td>
					<td style='padding: 8px;'>- MIT License facilitates the free use, modification, and distribution of the software, ensuring that users can leverage the codebase without restrictions<br>- It establishes the legal framework that protects both the authors and users, promoting collaboration and innovation within the project<br>- By providing this license, the project encourages community engagement while limiting liability for the authors.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/fsecada01/TextSpitter.git/blob/master/pyproject.toml'>pyproject.toml</a></b></td>
					<td style='padding: 8px;'>- Configuration settings streamline the linting, formatting, and packaging processes for the text-extraction application, TextSpitter<br>- By defining rules for code quality and style, it ensures consistency and maintainability across the codebase<br>- Additionally, it specifies project metadata, dependencies, and development tools, facilitating a smooth development experience and enhancing collaboration among contributors.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/fsecada01/TextSpitter.git/blob/master/requirements.txt'>requirements.txt</a></b></td>
					<td style='padding: 8px;'>- Manages project dependencies for a Python application by specifying required libraries and their versions<br>- Ensures compatibility and stability within the codebase, facilitating the installation of essential packages such as lxml, pymupdf, pypdf2, and python-docx<br>- This structure supports document processing and manipulation functionalities, contributing to the overall architectures efficiency and reliability.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/fsecada01/TextSpitter.git/blob/master/_config.yml'>_config.yml</a></b></td>
					<td style='padding: 8px;'>- Configures the Jekyll site to utilize the Cayman theme, enhancing the visual presentation and user experience of the project<br>- This setup plays a crucial role in defining the overall aesthetic and layout of the website, ensuring a cohesive and appealing design that aligns with the projects branding and purpose within the broader codebase architecture.</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- TextSpitter Submodule -->
	<details>
		<summary><b>TextSpitter</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ TextSpitter</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/fsecada01/TextSpitter.git/blob/master/TextSpitter\core.py'>core.py</a></b></td>
					<td style='padding: 8px;'>- FileExtractor serves as a core component for extracting and processing content from various file types, including text, CSV, DOCX, and PDF formats<br>- It standardizes file handling by providing methods to read and decode file contents while managing different input types<br>- This functionality enhances the overall architecture by enabling seamless integration of file processing capabilities within the broader application ecosystem.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/fsecada01/TextSpitter.git/blob/master/TextSpitter\logger.py'>logger.py</a></b></td>
					<td style='padding: 8px;'>- Enhancing application reliability through robust logging capabilities, the logger module facilitates a transition from basic print statements to a more sophisticated error capturing mechanism<br>- By integrating the loguru library, it ensures that error tracking is efficient and organized, ultimately contributing to improved debugging and maintenance across the entire codebase architecture.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/fsecada01/TextSpitter.git/blob/master/TextSpitter\main.py'>main.py</a></b></td>
					<td style='padding: 8px;'>- WordLoader serves as a central component in the application, facilitating the loading and processing of various file types through its integration with the FileExtractor<br>- By determining the appropriate extraction method based on file extensions and MIME types, it enhances the systems capability to handle diverse text formats, ensuring a seamless user experience while adhering to object-oriented design principles for future scalability.</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- .github Submodule -->
	<details>
		<summary><b>.github</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ .github</b></code>
			<!-- workflows Submodule -->
			<details>
				<summary><b>workflows</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ .github.workflows</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/fsecada01/TextSpitter.git/blob/master/.github\workflows\python-publish.yml'>python-publish.yml</a></b></td>
							<td style='padding: 8px;'>- Automates the process of publishing a Python package to a package registry upon the creation of a release<br>- By leveraging GitHub Actions, it ensures that the package is built and uploaded seamlessly, enhancing the overall workflow efficiency within the project<br>- This integration supports continuous delivery practices, allowing for streamlined updates and distribution of the software.</td>
						</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
</details>

---

## Getting Started

### Prerequisites

This project requires the following dependencies:

- **Programming Language:** Python
- **Package Manager:** Pip, Uv

### Installation

Build TextSpitter.git from the source and intsall dependencies:

1. **Clone the repository:**

    ```sh
    git clone https://github.com/fsecada01/TextSpitter.git
    ```

2. **Navigate to the project directory:**

    ```sh
    cd TextSpitter
    ```

3. **Install the dependencies:**

	```sh
	pip install -r core_requirements.txt dev_requirements.txt
	```
	**Using [uv](https://docs.astral.sh/uv/):**

	```sh
	uv sync --all-extras --dev
	```

### Usage

Run the project with:

**Using [pip](https://pypi.org/project/pip/):**
```sh
python {entrypoint}
```
**Using [uv](https://docs.astral.sh/uv/):**
```sh
uv run python {entrypoint}
```

### Testing

Textspitter.git uses the {__test_framework__} test framework. Run the test suite with:

**Using [pip](https://pypi.org/project/pip/):**
```sh
pytest
```
**Using [uv](https://docs.astral.sh/uv/):**
```sh
uv run pytest tests/
```

---

## Roadmap

* [x] spruce up documentation
* [X] Add stream functionality for s3-based file reading
* [x] expand functionality to other file types (e.g., code files, improved CSV handling)
* [ ] TDB

---

## Contributing

- **💬 [Join the Discussions](https://github.com/fsecada01/TextSpitter.git/discussions)**: Share your insights, provide feedback, or ask questions.
- **🐛 [Report Issues](https://github.com/fsecada01/TextSpitter.git/issues)**: Submit bugs found or log feature requests for the `TextSpitter.git` project.
- **💡 [Submit Pull Requests](https://github.com/fsecada01/TextSpitter.git/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your github account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/fsecada01/TextSpitter.git
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to github**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details closed>
<summary>Contributor Graph</summary>
<br>
<p align="left">
   <a href="https://github.com{/fsecada01/TextSpitter.git/}graphs/contributors">
      <img src="https://contrib.rocks/image?repo=fsecada01/TextSpitter.git">
   </a>
</p>
</details>

---

## License

Textspitter.git is protected under the [LICENSE](https://choosealicense.com/licenses) License. For more details, refer to the [LICENSE](https://choosealicense.com/licenses/) file.

---

## Acknowledgments

- Credit `contributors`, `inspiration`, `references`, etc.

<div align="right">

[![][back-to-top]](#top)

</div>


[back-to-top]: https://img.shields.io/badge/-BACK_TO_TOP-151515?style=flat-square


---
