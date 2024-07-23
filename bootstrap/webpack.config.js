const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CopyPlugin = require("copy-webpack-plugin");
const autoprefixer = require('autoprefixer')


module.exports = {
  mode: "development",
  entry: {
    main: './src/index.js'
  },
  devtool: 'inline-source-map',
  devServer: {
    static: './dist',
    client: {
      webSocketURL: 'ws://0.0.0.0:8080/frontend/ws',
    }
  },
  optimization: {
    runtimeChunk: 'single',
  },
  output: {
    filename: '[name].js',
    path: path.resolve(__dirname, 'dist'),
    clean: true,
    publicPath: '/frontend',
  },
  plugins: [
    new HtmlWebpackPlugin({ template: 'src/index.html' }),
    new CopyPlugin({
      patterns: [
        { from: "src/html", to: "." }
      ],
    }),
  ],
  module: {
    rules: [
      {
        test: /\.(scss)$/,
        use: [
          {
            // Adds CSS to the DOM by injecting a `<style>` tag
            loader: 'style-loader'
          },
          {
            // Interprets `@import` and `url()` like `import/require()` and will resolve them
            loader: 'css-loader'
          },
          {
            // Loader for webpack to process CSS with PostCSS
            loader: 'postcss-loader',
            options: {
              postcssOptions: {
                plugins: [
                  autoprefixer
                ]
              }
            }
          },
          {
            // Loads a SASS/SCSS file and compiles it to CSS
            loader: 'sass-loader'
          }
        ]
      }
    ]
  }
};
