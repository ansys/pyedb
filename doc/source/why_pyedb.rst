Why PyEDB?
==========

PyEDB represents a modern, decoupled approach to PCB design automation, offering significant advantages over traditional methods.

Server-Side Automation & Headless Operation
-------------------------------------------
The core innovation of PyEDB is its client-server architecture:

*   **PyEDB (Client):** A pure Python library you install and run in your environment.
*   **ansys-edb-core (Server):** A separate, high-performance gRPC service that handles all EDB operations.

This means you can **run PyEDB on a machine without a graphical user interface (GUI)**, such as:

*   **Linux servers** and high-performance computing (HPC) clusters.
*   **Docker containers** for consistent, reproducible environments.
*   **Cloud platforms** like AWS, Azure, or GCP.

This enables true **CI/CD (Continuous Integration/Continuous Deployment) for PCB design**. You can automate checks, simulations, and reports every time a design change is committed.

Performance and Integration
---------------------------
*   **Performance:** The gRPC protocol is fast and efficient, ideal for automating complex tasks and processing large designs.
*   **Python Ecosystem:** Being a pure Python client, PyEDB integrates seamlessly with the vast Python data science and machine learning stack (NumPy, Pandas, Matplotlib, Scikit-learn, PyTorch, etc.). You can easily post-process simulation results or use AI/ML to guide design decisions.

Use Cases
---------
*   **Automated Design Rule Checking (DRC):** Script checks for your team's specific design rules.
*   **Regression Testing:** Ensure a new design change doesn't break SI/PI/thermal performance.
*   **Parameter Sweeping:** Automatically analyze hundreds of variations of a design (e.g., via spacing, layer thickness).
*   **Batch Processing:** Extract S-parameters from a library of interconnects.
*   **Report Generation:** Automatically generate standardized PDF/HTML reports with plots and tables.