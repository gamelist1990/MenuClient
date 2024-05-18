/**
 * 
 */
package javaSoft;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicBoolean;

import javax.swing.JColorChooser;
import javax.swing.JDialog;
import javax.swing.JOptionPane;

import org.json.JSONObject;
import org.json.JSONTokener;

import javafx.animation.KeyFrame;
import javafx.animation.Timeline;
import javafx.application.Application;
import javafx.application.Platform;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.geometry.Rectangle2D;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.ContextMenu;
import javafx.scene.control.Label;
import javafx.scene.control.MenuItem;
import javafx.scene.control.Slider;
import javafx.scene.control.TextInputDialog;
import javafx.scene.input.MouseButton;
import javafx.scene.input.MouseEvent;
import javafx.scene.layout.Background;
import javafx.scene.layout.BackgroundFill;
import javafx.scene.layout.CornerRadii;
import javafx.scene.layout.Pane;
import javafx.scene.layout.VBox;
import javafx.scene.paint.Color;
import javafx.scene.shape.Circle;
import javafx.scene.shape.Rectangle;
import javafx.scene.shape.Shape;
import javafx.stage.Screen;
import javafx.stage.Stage;
import javafx.stage.StageStyle;
import javafx.util.Duration;













public class reload extends Application {

    private static Stage primaryStage;
    private Stage alphaStage;
    private Slider alphaSlider;
    private Label alphaLabel;
    private float alpha = 0.5f;
    private double xOffset = 0;
    private double yOffset = 0;
    private JSONObject config;
    private JSONObject defaultConfig;
    private List<Stage> stages = new ArrayList<>();
    private boolean espEnabled = false;
    private Process process = null;

    

    public static void main(String[] args) {
        launch(args);
    }

    public void showError(String title, String message) {
    JOptionPane.showMessageDialog(null, message, title, JOptionPane.ERROR_MESSAGE);
}
    public void showMessage(String title, String message) {
        JOptionPane.showMessageDialog(null, message, title, JOptionPane.PLAIN_MESSAGE);
    }


public void startNewWindow() {
        Stage primaryStage = new Stage();
        try {
            // ディスプレイの解像度を取得
            Rectangle2D screenBounds = Screen.getPrimary().getVisualBounds();

            // config.jsonから設定を読み込む
            JSONObject config = new JSONObject(new JSONTokener(new FileInputStream("config.json")));
            JSONObject circleConfig = config.getJSONObject("circle");
            String color = circleConfig.getString("color");
            int size = circleConfig.getInt("size");

            // 外側の円を作成（半径は設定から取得、色も設定から取得）
            Circle outerCircle = new Circle(size, Color.web(color));

            // 内側の円（ドーナツの穴）を作成（半径は設定から取得-1、色は透明）
            Circle innerCircle = new Circle(size - 1,Color.TRANSPARENT);

            // 外側の円から内側の円を引いてドーナツ型の形状を作成
            Shape donut = Shape.subtract(outerCircle, innerCircle);
            donut.setFill(outerCircle.getFill());


            // パネルを作成し、ドーナツ型の形状を追加
            Pane root = new Pane();
            root.setBackground(new Background(new BackgroundFill(Color.TRANSPARENT, CornerRadii.EMPTY, Insets.EMPTY)));
            root.getChildren().add(donut);

            // 透明の点を作成し、パネルの中心に配置
            Circle transparentDot = new Circle(0, Color.TRANSPARENT);
            root.getChildren().add(transparentDot);
            transparentDot.centerXProperty().bind(root.widthProperty().divide(2));
            transparentDot.centerYProperty().bind(root.heightProperty().divide(2));

            donut.layoutXProperty().bind(transparentDot.centerXProperty());
            donut.layoutYProperty().bind(transparentDot.centerYProperty());

            // ドーナツの形状が生成された後で中心点を更新
            donut.boundsInParentProperty().addListener((observable, oldValue, newValue) -> {
                donut.setTranslateX(-newValue.getWidth() / 2 + newValue.getWidth() / 2);
                donut.setTranslateY(-newValue.getHeight() / 2 + newValue.getHeight() / 2);
            });

            // シーンを作成し、パネルを追加
            Scene scene = new Scene(root, screenBounds.getWidth(), screenBounds.getHeight());

            // シーンの背景を透明に設定
            scene.setFill(Color.TRANSPARENT);

            // ステージにシーンを設定
            primaryStage.setScene(scene);

            // ステージのスタイルを設定（装飾なし、透明）
            primaryStage.initStyle(StageStyle.TRANSPARENT);

            // ステージを常に最前面にする
            primaryStage.setAlwaysOnTop(true);

            // ステージを表示
            primaryStage.show();
            stages.add(primaryStage);
        } catch(FileNotFoundException e) {
            e.printStackTrace();
        }
    }
public void stopWindow() {
    if (!stages.isEmpty()) {
        Stage stage = stages.get(stages.size() - 1); // 最後に追加されたStageを取得
        stage.close();
        stages.remove(stage); // リストから削除
    }
}

private void toggleESP() {
        if (espEnabled) {
            if (process != null) {
                process.destroy();
                process = null;
            }
            espEnabled = false;
            System.out.println("ESPを無効にしました。");
        } else {
            try {
                File currentDir = new File(System.getProperty("user.dir"));
                File script = new File(currentDir, "new.py");
                File pythonInterpreter = new File(currentDir, "venv/Scripts/python.exe");

                if (!script.exists()) {
                    showError("エラー", "new.pyが存在しません");
                } else if (!pythonInterpreter.exists()) {
                    showError("エラー", "Pythonのインタープリタが存在しません 付属のsetup.batを実行してください！！");
                } else {
                    ProcessBuilder pb = new ProcessBuilder(pythonInterpreter.getAbsolutePath(), script.getAbsolutePath());
                    process = pb.start();
                    espEnabled = true;
                    System.out.println("ESPを有効にしました。");
                }
            } catch (IOException e) {
                e.printStackTrace();
                showError("エラー", "ESPの起動に失敗しました");
            }
        }
    }



 


    @Override
    public void start(Stage primaryStage) {
        reload.primaryStage = primaryStage;
        initializeDefaultConfig();
        loadOrCreateConfig();
        loadWindowPosition();

        primaryStage.setTitle("Menu Window");
        primaryStage.initStyle(StageStyle.TRANSPARENT);
        primaryStage.setOpacity(alpha);

        primaryStage.setOnShown(event -> {
        primaryStage.requestFocus();
        primaryStage.setAlwaysOnTop(true);

    });

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
        
        Rectangle separator = new Rectangle();
        separator.setWidth(160);  // メニューの幅に合わせて調整
        separator.setHeight(1);  // 細い横棒なので高さは1
        separator.setFill(Color.WHITE);  // 横棒の色を白に設定
        vbox.getChildren().add(separator);
        
        Timeline fiveSecondsWonder = new Timeline(
        	    new KeyFrame(Duration.seconds(5), event -> saveWindowPosition())
        	);
        	fiveSecondsWonder.setCycleCount(Timeline.INDEFINITE);
        	fiveSecondsWonder.play();


        
        



AtomicBoolean isRunning = new AtomicBoolean(false);

Button circleButton = createButton("画面に円を設置", event -> {
    if (isRunning.get()) {
        stopWindow();
    } else {
        startNewWindow();
    }
    isRunning.set(!isRunning.get());
});
VBox.setMargin(circleButton, new Insets(30, 0, 0, 0));

setupCircleButtonContextMenu(circleButton);





    @SuppressWarnings("deprecation")
Button startButton = createButton("アプリ起動", event -> {
	
    // Start app logic here
    String programPath = config.getJSONObject("program_path").toString();
    if (!programPath.isEmpty()) {
        File file = new File(programPath);
        if (file.exists() && !file.isDirectory()) {
            String extension = "";

            int i = programPath.lastIndexOf('.');
            if (i > 0) {
                extension = programPath.substring(i+1);
            }
            if (extension.equals("exe") || extension.equals("lnk")) {
                try {
                    Runtime.getRuntime().exec(programPath);
                } catch (IOException e) {
                    e.printStackTrace();
                }
            } else {
                showError("エラー","指定されたパスは実行可能なアプリケーションを指していません");
            }
        } else {
            showError("エラー", "指定されたパスが存在しません");
        }
    }
});
setupStartButtonContextMenu(startButton);



        Button espButton = createButton("ESP/[使用して良いか確認]", event -> toggleESP());




        Button alphaButton = createButton("透明度調整", event -> openAlphaWindow());

        Button overviewButton = createButton("概要", event -> {
        	showMessage("概要v.0.1[java]","MenuClientのJava版ですPythonとの違う点は自分で探してください\n開発者はこう君(1人)です");
        });

        VBox.setMargin(overviewButton, new Insets(0, 0, 30, 0));

        Button exitButton = createButton("アプリを終了", event -> System.exit(0));

        vbox.getChildren().addAll(circleButton, startButton, espButton, alphaButton, overviewButton, exitButton);

        Scene scene = new Scene(vbox, 160, 350);
        primaryStage.setScene(scene);
        primaryStage.show();
        
    }

    
    private void setupStartButtonContextMenu(Button startButton) {
    ContextMenu contextMenu = new ContextMenu();

    MenuItem pathItem = new MenuItem("プログラムのパスを設定");
    pathItem.setOnAction(event -> {
        TextInputDialog dialog = new TextInputDialog("");
        dialog.setTitle("プログラムのパス設定");
        dialog.setHeaderText("新しいプログラムのパスを入力してください:");
        dialog.setContentText("パス:");

        Optional<String> result = dialog.showAndWait();
        result.ifPresent(path -> {
            config.put("program_path", path);
            saveConfig();
        });
    });

    contextMenu.getItems().addAll(pathItem);

    startButton.addEventHandler(MouseEvent.MOUSE_CLICKED, (MouseEvent event) -> {
        if (event.getButton() == MouseButton.SECONDARY) {
            contextMenu.show(startButton, event.getScreenX(), event.getScreenY());
        }
    });
}


private void saveWindowPosition() {
    JSONObject windowPosition = new JSONObject();
    windowPosition.put("x", primaryStage.getX());
    windowPosition.put("y", primaryStage.getY());
    config.put("window_position", windowPosition);
    saveConfig();
}

private void loadWindowPosition() {
    JSONObject windowPosition = config.getJSONObject("window_position");
    double x = windowPosition.getDouble("x");
    double y = windowPosition.getDouble("y");
    primaryStage.setX(x);
    primaryStage.setY(y);
}


private void initializeDefaultConfig() {
    defaultConfig = new JSONObject();
    JSONObject circle = new JSONObject();
    circle.put("color", "white");
    circle.put("size", 50);

    JSONObject windowPosition = new JSONObject();
    windowPosition.put("x", 100);
    windowPosition.put("y", 100);

    defaultConfig.put("circle", circle);
    defaultConfig.put("alpha", 0.5); // alpha value added to default config
    defaultConfig.put("program_path", new JSONObject());
    defaultConfig.put("menu_color", "black");
    defaultConfig.put("window_position", windowPosition);
}

    private void loadOrCreateConfig() {
    try {
        FileReader reader = new FileReader("config.json");
        config = new JSONObject(new JSONTokener(reader));
        alpha = config.getFloat("alpha"); // Load alpha value from config
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
     // ボタンが押されたときのスタイルを設定
        button.setOnMousePressed(event -> button.setStyle("-fx-background-color: #7d7d7d; -fx-text-fill: white;"));

        // ボタンが離されたときのスタイルを設定（元のスタイルに戻す）
        button.setOnMouseReleased(event -> button.setStyle("-fx-background-color: #4d4d4d; -fx-text-fill: white;"));
        return button;
    }

    private void setupCircleButtonContextMenu(Button circleButton) {
        ContextMenu contextMenu = new ContextMenu();

        MenuItem colorItem = new MenuItem("色を変更");
        colorItem.setOnAction(event -> {
    Platform.runLater(() -> {
        final JColorChooser colorChooser = new JColorChooser();
        final JDialog dialog = JColorChooser.createDialog(null, "色を変更", true, colorChooser, e -> {
            java.awt.Color newColor = colorChooser.getColor();
            config.getJSONObject("circle").put("color", "#" + Integer.toHexString(newColor.getRGB()).substring(2));
            saveConfig();
        }, null);
        dialog.setVisible(true);
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
    config.put("alpha", alpha); // Save alpha value to config
    saveConfig();
}
}
