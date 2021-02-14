const path = require('path')
const webpack = require('webpack')
module.exports = {
    // Where Webpack looks to load your JavaScript
    entry: {
        app: path.resolve(__dirname, 'src/app/index.tsx'),
    },
    mode: 'development',
    // Where Webpack spits out the results (the myapp static folder)
    output: {
        path: path.resolve(__dirname, '../static/lumber/build/'),
        filename: '[name].js',
    },
    plugins: [
        // Don't output new files if there is an error
        new webpack.NoEmitOnErrorsPlugin(),
    ],
    // Add a rule so Webpack reads JS with Babel
    module: {
        rules: [
            {
                test: /\.tsx?$/,
                use: 'ts-loader',
                exclude: /node_modules/,
            },
            {
                enforce: 'pre',
                test: /\.js$/,
                loader: "source-map-loader",
            }
        ]
    },

    // Where find modules that can be imported (eg. React)
    resolve: {
        extensions: ['.js', '.jsx', '.ts', '.tsx'],
        modules: [
            path.resolve(__dirname, 'src'),
            path.resolve(__dirname, 'node_modules'),
        ],
    },
}

