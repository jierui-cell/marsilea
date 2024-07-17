<p align="center">
  <picture align="center">
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/Marsilea-viz/marsilea/raw/main/img/banner-dark.jpg">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/Marsilea-viz/marsilea/raw/main/img/banner-blue.jpg">
    <img alt="Shows a bar chart with benchmark results." src="https://github.com/Marsilea-viz/marsilea/raw/main/img/banner-dark.jpg" width="400">
  </picture>
</p>

[![Documentation Status](https://img.shields.io/readthedocs/marsilea?color=57B77E&logo=readthedocs&logoColor=white&style=flat-square)](https://marsilea.readthedocs.io/en/stable)
![pypi version](https://img.shields.io/pypi/v/marsilea?color=0098FF&logo=python&logoColor=white&style=flat-square)
![PyPI - License](https://img.shields.io/pypi/l/marsilea?color=FFD43B&style=flat-square)

# Marsilea: Declarative creation of composable visualization!

---

## Documentation

You can read the documentation on Read the Docs.

[Read Documentation](https://marsilea.readthedocs.io/)

## Installation

```shell
pip install marsilea
```

## What is Composable Visualization?

<p align="center">
  <picture align="center">
    <img alt="Shows a bar chart with benchmark results." src="https://github.com/Marsilea-viz/marsilea/raw/main/img/showcase.gif" width="300">
  </picture>
</p>

When we do visualization, we often need to combine multiple plots to show different aspects of the data.
For example, we may need to create a heatmap to show the expression of genes in different cells,
and then create a bar chart to show the expression of genes in different cell types.
A visualization contains multiple plots is called a composable visualization.
In Marsilea, we employ a declarative approach for user to create composable visualization incrementally.

## Examples

<table>
    <thead>
        <tr>
            <th>
                <a href="https://marsilea.readthedocs.io/en/latest/examples/Gallery/plot_tiobe_index.html">
                    Bar Chart With Image
                </a>
            </th>
            <th>
                <a href="https://marsilea.readthedocs.io/en/latest/examples/Gallery/plot_oil_well.html">
                    Stacked Bar
                </a>
            </th>
            <th>
                <a href="https://marsilea.readthedocs.io/en/latest/examples/Gallery/plot_arc_diagram.html">
                    Arc Diagram
                </a>
            </th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>
                <img src="https://marsilea.readthedocs.io/en/latest/_images/sphx_glr_plot_tiobe_index_001_2_00x.png" height="300px">
            </td>
            <td>
                <img src="https://marsilea.readthedocs.io/en/latest/_images/sphx_glr_plot_oil_well_001_2_00x.png" height="300px">
            </td>
            <td>
                <img src="https://marsilea.readthedocs.io/en/latest/_images/sphx_glr_plot_arc_diagram_001_2_00x.png" width="300px">
            </td>
        </tr>
    </tbody>
</table>

<table>
    <thead>
        <tr>
            <th>
                <a href="https://marsilea.readthedocs.io/en/latest/examples/Gallery/plot_pbmc3k.html">
                    Heatmap
                </a>
            </th>
            <th>
                <a href="https://marsilea.readthedocs.io/en/latest/examples/Gallery/plot_oncoprint.html">
                    Oncoprint
                </a>
            </th>
            <th>
                <a href="https://marsilea.readthedocs.io/en/latest/examples/Gallery/plot_upset.html">
                    Upsetplot
                </a>
            </th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>
                <img src="https://marsilea.readthedocs.io/en/latest/_images/sphx_glr_plot_pbmc3k_001_2_00x.png" width="300px">
            </td>
            <td>
                <img src="https://marsilea.readthedocs.io/en/latest/_images/sphx_glr_plot_oncoprint_005_2_00x.png" width="300px">
            </td>
            <td>
                <img src="https://marsilea.readthedocs.io/en/latest/_images/sphx_glr_plot_upset_001_2_00x.png" width="300px">
            </td>
        </tr>
    </tbody>
</table>
