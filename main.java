package com.fasterxml.jackson.databind;

import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Optional;

import org.json.JSONObject;
import org.json.JSONTokener;

import javafx.application.Application;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.geometry.Rectangle2D;
import javafx.scene.Group;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.ColorPicker;
import javafx.scene.control.ContextMenu;
import javafx.scene.control.Label;
import javafx.scene.control.MenuItem;
import javafx.scene.control.Slider;
import javafx.scene.control.TextInputDialog;
import javafx.scene.input.MouseButton;
import javafx.scene.input.MouseEvent;
import javafx.scene.layout.VBox;
import javafx.scene.paint.Color;
import javafx.scene.shape.Circle;
import javafx.scene.shape.Shape;
import javafx.stage.Screen;
import javafx.stage.Stage;
import javafx.stage.StageStyle;

public class hello extends Application {

    private static Stage primaryStage;
    private Stage alphaStage;
    private Stage circleStage; // Add this line
    private Slider alphaSlider;
    private Label alphaLabel;
    private float alpha = 0.5f;
    private double xOffset = 0;
    private double yOffset = 0;
    private JSONObject config;
    private JSONObject defaultConfig;

    public static void main(String[] args) {
        launch(args);
    }

    @Override
    public void start(Stage primaryStage) {
        hello.primaryStage = primaryStage;
        initializeDefaultConfig();
        loadOrCreateConfig();

        primaryStage.setTitle("Menu Window");
        primaryStage.initStyle(StageStyle.TRANSPARENT);
        primaryStage.setOpacity(alpha);

        VBox vbox = new VBox();
        vbox.setPadding(new Insets(20));
        vbox.setSpacing(10);
        vbox.setAlignment(Pos.CENTER);
        vbox.setStyle("-fx-background-color: #2d2d2d; -fx-text-fill: white;");

        vbox.setOnMousePressed(event -> {
            xOffset = event.getSceneX();
            yOffset = event.getSceneY();
        });

        vbox.setOnMouseDragged(event -> {
            primaryStage.setX(event.getScreenX() - xOffset);
            primaryStage.setY(event.getScreenY() - yOffset);
        });

        Label menuClientLabel = new Label("MenuClient");
        menuClientLabel.setStyle("-fx-text-fill: white; -fx-font-size:20px;");
        vbox.getChildren().add(menuClientLabel);
        VBox.setMargin(menuClientLabel, new Insets(0, 0, 30, 0));
        
        
        

        Button circleButton = createButton("画面に円を設置", event -> {
            // Load the latest config
            loadOrCreateConfig();

            // Draw circle logic here
            if (!config.getJSONObject("circle").getBoolean("window_exists")) {
                // Create a new stage for the circle
                circleStage = new Stage();
                circleStage.initStyle(StageStyle.TRANSPARENT);

                // Create a new circle with the color and size from the config
                Circle outerCircle = new Circle();
                outerCircle.setFill(Color.valueOf(config.getJSONObject("circle").getString("color")));
                outerCircle.setRadius(config.getJSONObject("circle").getInt("size"));

                // Create an inner circle
                Circle innerCircle = new Circle();
                innerCircle.setRadius(config.getJSONObject("circle").getInt("size") * 0.75); // Adjust as needed

                // Subtract the inner circle from the outer circle to create a donut shape
                Shape donut = Shape.subtract(outerCircle, innerCircle);

                // Create a new scene with the donut and set it to the stage
                Scene circleScene = new Scene(new Group(donut));
                circleScene.setFill(Color.TRANSPARENT);
                circleStage.setScene(circleScene);

                // Position the circle stage so that the circle is in the center of the screen
                Rectangle2D screenBounds = Screen.getPrimary().getVisualBounds();
                circleStage.setX(screenBounds.getWidth() / 2 - outerCircle.getRadius() * 2);
                circleStage.setY(screenBounds.getHeight() / 2 - outerCircle.getRadius() * 2);

                // Show the circle stage
                circleStage.show();

                // Update the config to show that the circle window now exists and is visible
                config.getJSONObject("circle").put("window_exists", true);
                config.getJSONObject("circle").put("visible", true);
            } else if (circleStage != null) {
                // If the circle window already exists, check if it is visible
                if (config.getJSONObject("circle").getBoolean("visible")) {
                    // If the circle window is visible, hide it
                    circleStage.hide();

                    // Update the config to show that the circle is now hidden
                    config.getJSONObject("circle").put("visible", false);
                } else {
                    // If the circle window is not visible, show it
                    circleStage.show();

                    // Update the config to show that the circle is now visible
                    config.getJSONObject("circle").put("visible", true);
                }
            }

            // Save the updated config
            saveConfig();
        });
        setupCircleButtonContextMenu(circleButton);


        








        Button startButton = createButton("配信スタート", event -> {
            // Start broadcast logic here
        });

        Button espButton = createButton("ESP/[使用して良いか確認]", event -> {
            // ESP logic here
        });

        Button alphaButton = createButton("透明度調整", event -> openAlphaWindow());

        Button overviewButton = createButton("概要", event -> {
            // Show overview logic here
        });

        VBox.setMargin(overviewButton, new Insets(0, 0, 30, 0));

        Button exitButton = createButton("アプリを終了", event -> System.exit(0));

        vbox.getChildren().addAll(circleButton, startButton, espButton, alphaButton, overviewButton, exitButton);

        Scene scene = new Scene(vbox, 160, 350);
        primaryStage.setScene(scene);
        primaryStage.show();
    }

    private void initializeDefaultConfig() {
        defaultConfig = new JSONObject();
        JSONObject circle = new JSONObject();
        circle.put("window_exists", false);
        circle.put("visible", false);
        circle.put("color", "white");
        circle.put("size", 50);
        circle.put("antialiasing", false);

        JSONObject windowPosition = new JSONObject();
        windowPosition.put("x", 681);
        windowPosition.put("y", 87);

        defaultConfig.put("circle", circle);
        defaultConfig.put("alpha", 0.5);
        defaultConfig.put("program_path", new JSONObject());
        defaultConfig.put("menu_color", "black");
        defaultConfig.put("window_position", windowPosition);
    }

    private void loadOrCreateConfig() {
        try {
            FileReader reader = new FileReader("config.json");
            config = new JSONObject(new JSONTokener(reader));
        } catch (Exception e) {
            config = defaultConfig;
            saveConfig();
        }
    }

    private void saveConfig() {
        try (FileWriter file = new FileWriter("config.json")) {
            file.write(config.toString(4)); // Indent with four spaces for readability
            file.flush();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private Button createButton(String text, EventHandler<ActionEvent> eventHandler) {
        Button button = new Button(text);
        button.setOnAction(eventHandler);
        button.setStyle("-fx-background-color: #4d4d4d; -fx-text-fill: white;");
        return button;
    }

    private void setupCircleButtonContextMenu(Button circleButton) {
        ContextMenu contextMenu = new ContextMenu();

        MenuItem colorItem = new MenuItem("色を変更");
        colorItem.setOnAction(event -> {
            ColorPicker colorPicker = new ColorPicker();
            colorPicker.setValue(Color.valueOf(config.getJSONObject("circle").getString("color")));
            colorPicker.show();

            colorPicker.setOnAction(e -> {
                Color newColor = colorPicker.getValue();
                config.getJSONObject("circle").put("color", "#" + newColor.toString().substring(2, 8));
                saveConfig();
            });
        });

        MenuItem sizeItem = new MenuItem("サイズを変更");
        sizeItem.setOnAction(event -> {
            TextInputDialog dialog = new TextInputDialog(config.getJSONObject("circle").get("size").toString());
            dialog.setTitle("サイズ変更");
            dialog.setHeaderText("新しいサイズを入力してください:");
            dialog.setContentText("サイズ:");

            Optional<String> result = dialog.showAndWait();
            result.ifPresent(size -> {
                config.getJSONObject("circle").put("size", Integer.parseInt(size));
                saveConfig();
            });
        });

        contextMenu.getItems().addAll(colorItem, sizeItem);

        circleButton.addEventHandler(MouseEvent.MOUSE_CLICKED, (MouseEvent event) -> {
            if (event.getButton() == MouseButton.SECONDARY) {
                contextMenu.show(circleButton, event.getScreenX(), event.getScreenY());
            }
        });
    }

    private void openAlphaWindow() {
        alphaStage = new Stage();
        alphaStage.initStyle(StageStyle.UTILITY);

        VBox vbox = new VBox();
        vbox.setPadding(new Insets(10));
        vbox.setSpacing(8);

        alphaSlider = new Slider(0, 1, alpha);
        alphaSlider.setShowTickLabels(true);
        alphaSlider.setShowTickMarks(true);
        alphaSlider.valueProperty().addListener((observable, oldValue, newValue) -> changeAlpha(newValue.floatValue()));

        alphaLabel = new Label("現在の透明度: " + alpha);

        vbox.getChildren().addAll(alphaSlider, alphaLabel);

        Scene scene = new Scene(vbox, 200, 100);
        alphaStage.setScene(scene);
        alphaStage.show();
    }

    private void changeAlpha(float value) {
        alpha = Math.max(value, 0.10f);
        primaryStage.setOpacity(alpha);
        alphaLabel.setText("現在の透明度: " + alpha);
    }
}